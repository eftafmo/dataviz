<!--
     this is the base for both regular components and root components.
     derived components must set up a "props" property, either as prop or data.
 -->

<script>
import Vue from 'vue';
import * as d3 from 'd3';
import {FILTERS, Q} from '../globals.js'
import {colour2gray} from 'js/lib/util';


export default Vue.extend({
  beforeCreate() {
    // adding the queue here since it needs not be observable
    this.queue = Q;
  },

  props: {
    initial: [Object, Array],
  },

  data() {
    return {
      filters: FILTERS,

      // what the dataset can be filtered on.
      // default to filters applicable to all scenarios.
      filter_by: [
        "fm", "beneficiary",
        "sector", "area",
      ],

      // aggregation columns.
      aggregate_by: [],
      // default to columns common to all scenarios.
      aggregate_on: [
        'allocation',
        {source: 'beneficiary', destination: 'beneficiaries',
         type: String, filter_by: 'is_not_ta'},
        {source: 'sector', destination: 'sectors',
         type: String, filter_by: 'is_not_ta'},
        {source: 'area', destination: 'areas',
         type: String, filter_by: 'is_not_ta'},
        // TODO: Partners doesn't have "programmes". Fix.
        {source: 'programmes',
         type: Object, filter_by: 'is_not_ta'},
      ],

      // this is only used internally. we can't come up with a nicer name,
      // because properties beginning with underscore aren't reactive
      dataset__: null,

      // opacity of filtered-out items
      inactive_opacity: .7,

      locale: {
        // see https://github.com/d3/d3-format/blob/master/locale/
        // TODO: derive and extend the browser locale?
        // useful characters: nbsp: "\u00a0", narrow nbsp: "\u202f"
        "decimal": ",", // that's the european way
        "thousands": "\u00A0", // nbsp
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

    inactivecolour() {
      return (
        (c) => colour2gray(c, this.inactive_opacity)
      );
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

    filtered() {
      return this.filter(this.dataset, this.filter_by);
    },

    aggregated() {
      return this.aggregate(this.filtered, this.aggregate_by, this.aggregate_on);
    },

    data() {
      // convenience property, should be overriden by each component
      return this.filtered;
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
    //this works only for strings that gain an 's' at the end for plural
    singularize(str, value) {
      let lastchar = str.substring(str.length-1, str.length);
      if (value == 1 && lastchar == 's')
        str = str.substring(0, str.length-1);
      return str
    },

    aggregate(data, by, on, flatten=false) {
      /*
         by: array of columns names to aggregate by,
         on: array of columns names to aggregate on,
         flatten: whether to return the data as an array.
                  defaults to false (returns the raw tree).

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

          if (type === Number) {
            // numbers are added together
            if (current === undefined)
              current = row[dstcol] = 0;

            if (filter_by && !item[filter_by]) {
              continue;
            }

            row[dstcol] = current + value;
          }
          else if (type === String || type === Array || type === Object) {
            // strings, arrays items and object keys are consolidated into sets
            if (current === undefined)
              current = row[dstcol] = d3.set();

            if (filter_by && !item[filter_by]) {
              continue;
            }

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

    main() {
      /*
       * main entry point, only called on ready
       */

      // no need to throw, some components could be Vue-only
      //throw "Base.main(): Not implemented";
    },

    fetchData() {
      if (!this.datasource) throw "Base.fetchData(): Missing datasource."

      d3.json(this.datasource, (error, ds) => {
        if (error) throw error;
        this.dataset = ds;
      });
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
    'isReady': 'main',

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
});
</script>
