<style lang="less">
@duration: .5s;

.fade-enter-active, .fade-leave-active {
  transition: opacity @duration;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>


<script>
import * as d3 from 'd3';
import {FILTERS, Q} from '../../globals.js'

export default {
  beforeCreate() {
    // adding the queue here since it needs not be observable
    this.queue = Q;
  },

  props: {
    datasource: String, // TODO: required?
    initial: [Object, Array],
  },

  data() {
    return {
      filters: FILTERS,

      // this is only used internally. we can't come up with a nicer name,
      // because properties beginning with underscore aren't reactive
      dataset__: null,

      locale: {
        // see https://github.com/d3/d3-format/blob/master/locale/
        // TODO: derive and extend the browser locale?
        // useful characters: nbsp: "\u00a0", narrow nbsp: "\u202f"
        "decimal": ",", // that's the european way
        "thousands": ".", // dot, the european way
        "grouping": [3],
        "currency": ["€", ""],
        "percent": "%",
      },

      // helper for transitions
      changed: false,
    };
  },

  computed: {
    currency() {
      // show currency. thousand separators. decimal int.
      const format = "$,d";

      return d3.formatLocale(this.locale).format(format);
    },
    number() {
      const format = ",d";
      return d3.formatLocale(this.locale).format(format);
    },

    dataset: {
      // make dataset a settable computed
      get() {
        return this.dataset__ || this.initial;
      },
      set(val) {
        this.dataset__ = val;
      },
    },

    data() {
      // convenience property, should be overriden by each component
      return this.dataset;
    },

    hasData() {
      return !!(this.dataset
                // safeguard because empty vue observables evaluate to true
                && Object.keys(this.dataset).length);
    },
    isReady() {
      return !!(this.hasData
                && this.$el);
    },
  },

  created() {
    // fetch data only if no initial data provided,
    // and there is an external datasource
    if (!this.hasData && this.datasource) this.fetchData();
  },

  mounted() {
  },

  methods: {
    _mkfilterfuncs(filters) {
      // returns an array of filtering functions, given a set of filter names
      // and considering the filters currently set
      if (!filters) filters = d3.keys(this.filters);

      const filterfuncs = [];
      for (const f of filters) {
        const val = this.filters[f];
        if (!val) continue;

        filterfuncs.push(
          // NOTE: use lower-case comparison, or things might get messy
          // (until we switch to using ids)
          (item) => item[f] && item[f].toLowerCase() == val.toLowerCase()
        );
      }

      return filterfuncs;
    },

    // TODO: change this to take the list of excluded filters instead.
    // that's how every component uses it anyway.
    filter(data, filters) {
      const filterfuncs = this._mkfilterfuncs(filters);
      if (!filterfuncs) return data;

      const filterfunc = (item) => {
        for (const func of filterfuncs) {
          if (!func(item)) return false;
        }
        return true;
      }

      return data.filter(filterfunc);
    },

    aggregate(data, by, on, flatten=true) {
      /*
         by: array of columns names to aggregate by,
         on: array of columns names to aggregate on,
         flatten: whether to return the data as an array or the raw tree.

         a column spec can be either a string or an object of the form
         {
           source: 'input_column_name',
           destination: 'output_column_name',
         }
         `columns` also take a `type` property, which defaults to Number
           and a `filter_by` property, which expects boolean values (false and undefined rows are excluded)
       */

      const bycols = {};
      for (const col of by) {
        let src, dst;
        if (typeof col == 'string') {
          src = dst = col;
        } else {
          src = col.source;
          dst = col.destination;

          if (dst === undefined) dst = src;
        }

        bycols[src] = dst;
      }
      const _bycols = Object.keys(bycols);

      const oncols = {};
      for (const col of on) {
        let src, dst, type, filter_by;
        if (typeof col == 'string') {
          src = dst = col;
          type = Number;
        } else {
          src = col.source;
          dst = col.destination;
          type = col.type;
          filter_by = col.filter_by;

          if (dst === undefined) dst = src;
          if (type === undefined) type = Number;
        }

        oncols[src] = {destination: dst, type: type, filter_by: filter_by};
      };

      // each aggreggation level is a sub-dictionary,
      // each aggreggation item a key.
      const aggregator = {};

      for (const item of data) {
        const base = {};
        let row = aggregator;
        for (let i=0, j=_bycols.length; i<j; i++) {
          const srccol = _bycols[i],
                dstcol = bycols[srccol],
                value = item[srccol];

          base[dstcol] = value;

          if (row[value] === undefined)
            row[value] = i == j - 1 ? base : {};

          row = row[value];
        }

        for (const srccol in oncols) {
          const _col = oncols[srccol],
                dstcol = _col.destination,
                type = _col.type,
                filter_by = _col.filter_by,
                value = type == Number ? Number(item[srccol]) : item[srccol];

          let current = row[dstcol];

          if (filter_by && !item[filter_by]) {
            continue;
          }

          if (type === Number) {
            // numbers are added together
            if (current === undefined)
              current = row[dstcol] = 0;

            row[dstcol] = current + value;
          }
          else if (type === String || type === Array || type === Object) {
            // strings, arrays items and object keys are consolidated into sets
            if (current === undefined)
              current = row[dstcol] = d3.set();

            if (type === String) {
              current.add(value);
            }
            else if (type === Array) {
              for (const v of value) {
                current.add(v);
              }
            }
            else if (type === Object) {
              for (const k in value) {
                current.add(k);
              }
            }
          }
          else console.warn(srccol, ":: unkwown type", type);
        }
      }

      if (!flatten) return aggregator;

      const out = [],
            levels = by.length;

      function recurse(obj, level) {
        if (level == levels) {
          out.push(obj);
          return;
        }
        for (const k in obj) {
          recurse(obj[k], level + 1);
        }
      }

      recurse(aggregator, 0);
      return out;
    },

    _main() {
      this.beforeMain();
      this.main();
    },
    beforeMain() {
      /*
       * some components will want to run initialisation code
       * when data becomes available, but before main.
       * this is the place to do it.
       */
      return;
    },

    main() {
      /*
       * main entry point.
       * implementations need to make sure this only gets called on ready
       */

      // no need to throw, some components could be Vue-only
      //throw "Base.main(): Not implemented";
    },

    fetchData() {
      if (!this.datasource) throw "Base.fetchData(): Missing datasource."

      d3.json(this.datasource, (error, ds) => {
        if (error) throw error;
        this.dataset = this.processDataset(ds);
      });
    },

    processDataset(ds) {
      /*
       * preliminary processing of initial data.
       * override it as needed.
       */

      return ds;
    },

    /*
     * filter-related methods
     */
    handleFilter(type, val, old) {
      // this should be handled by each component specifically
      return
      //throw "Unhandled filter: " + type;
      //console.log(`» [${type}] filter:`, old,'→', val);
    },
    handleFilterFm(val, old) {
      const type = "fm";
      this.handleFilter(type, val, old);
    },
    handleFilterBeneficiary(val, old) {
      const type = "beneficiary";
      this.handleFilter(type, val, old);
    },
    handleFilterSector(val, old) {
      const type = "sector";
      this.handleFilter(type, val, old);
    },
    handleFilterArea(val, old) {
      const type = "area";
      this.handleFilter(type, val, old);
    },
  },
  watch: {
    'isReady': '_main',

    // make sure every key exists from the start
    'filters.fm': 'handleFilterFm',
    'filters.beneficiary': 'handleFilterBeneficiary',
    'filters.sector': 'handleFilterSector',
    'filters.area': 'handleFilterArea',

    // this one is used only for vue transitions
    'filters': {
      deep: true,
      handler() {
        this.changed = !this.changed;
      },
    },
  },
};
</script>
