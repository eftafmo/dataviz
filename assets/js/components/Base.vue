<!--
     this is the base for both regular components and root components.
     derived components must set up a "props" property, either as prop or data.
 -->

<script>
import BaseMixin from "./mixins/Base";
import WithFiltersMixin, { setFilters } from "./mixins/WithFilters";
import { getAssetUrl } from "../lib/util";

export default {
  mixins: [BaseMixin, WithFiltersMixin],

  props: {
    initial: {
      type: [Object, Array],
      default: null,
    },
    datasourcePeriods: {
      type: Array,
      default: () => [],
      required: false,
    },
    embedScenario: {
      type: String,
      default: null,
      required: false,
    },
  },

  data() {
    return {
      // what the dataset can be filtered on.
      // default to filters applicable to all scenarios.
      filter_by: ["fm", "beneficiary", "sector", "area", "sdg_no", "thematic"],

      // aggregation columns.
      aggregate_by: [],
      // default to columns common to all scenarios.
      aggregate_on: [
        "allocation",
        "net_allocation",
        {
          source: "beneficiary",
          destination: "beneficiaries",
          type: String,
          exclude: "is_ta",
        },
        {
          source: "sector",
          destination: "sectors",
          type: String,
          exclude: "is_ta",
        },
        {
          source: "area",
          destination: "areas",
          type: String,
          exclude: "is_ta",
        },
        { source: "programmes", type: Object },
      ],

      // this is only used internally. we can't come up with a nicer name,
      // because properties beginning with underscore aren't reactive
      dataset__: null,

      // helper for transitions
      changed: 0,
    };
  },

  computed: {
    dataset: {
      // make dataset a settable computed
      get() {
        return this.dataset__ || this.initial || [];
      },
      set(val) {
        this.dataset__ = val;
      },
    },

    filtered() {
      return this.filter(this.dataset, this.filter_by);
    },

    aggregated() {
      return this.aggregate(
        this.filtered,
        this.aggregate_by,
        this.aggregate_on,
      );
    },

    data() {
      // convenience property, should be overriden by each component
      return this.filtered;
    },

    hasData() {
      return !!(
        this.dataset &&
        // safeguard because empty vue observables evaluate to true
        Object.keys(this.dataset).length
      );
    },
    isReady() {
      return !!(this.hasData && this.is_mounted);
    },
  },
  watch: {
    isReady: "main",
    // this one is used only for vue transitions
    filters: {
      deep: true,
      handler() {
        this.changed = Number(!this.changed);
      },
    },
  },
  beforeCreate() {
    // Set filters from the opts given by the generated JS
    // file. As we don't have access to the URL where this
    // was loaded from while embedded.
    if (this.opts && this.period && this.embedScenario) {
      setFilters(this.embedScenario, this.period, this.opts);
    }
  },
  created() {
    // fetch data only if no initial data provided,
    // and there is an external datasource
    if (!this.hasData && this.datasource) this.fetchData();
  },

  methods: {
    isHungaryException(countryId) {
      // An agreement with Hungary was not reached for this period.
      return this.period === "2014-2021" && countryId.slice(0, 2) === "HU";
    },
    getBeneficiaryCount(beneficiaries) {
      // Exclude "Non-country specific"
      return Array.from(beneficiaries || []).filter(
        (countryCode) => countryCode !== "XX",
      ).length;
    },
    async fetchData() {
      if (!this.datasource) throw "Base.fetchData(): Missing datasource.";

      const responses = await Promise.all(
        this.datasourcePeriods.map(this.loadPeriod),
      );
      const data = [].concat(...responses);
      this.dataset = Object.freeze(data);
    },
    async loadPeriod(period) {
      const url = new URL(this.datasource, window.location);
      url.searchParams.append("period", period);
      const dataset = await (await fetch(url.toString())).json();

      // Set the period for each item, for cases where the backend doesn't
      // include this information. Makes grouping and filtering easier along
      // the line.
      dataset.forEach((item) => {
        item.period = period;
      });
      return dataset;
    },
    getAssetUrl(path) {
      return getAssetUrl(path, this.origin || this.$.root.props.origin);
    },
    _mkfilterfuncs(filters) {
      // returns an array of filtering functions, given a set of filter names
      // and considering the filters currently set
      if (!filters) filters = Object.keys(this.filters);

      const filterfuncs = [];
      for (const f of filters) {
        let val = this.filters[f];
        if (!val) continue;

        if (f === "beneficiary" && (val === "GR" || val === "EL")) {
          switch (this.period) {
            case "2004-2009":
            case "2009-2014":
              val = "GR";
              break;
            case "2014-2021":
            default:
              val = "EL";
              break;
          }
        }

        filterfuncs.push(
          // NOTE: use lower-case comparison, or things might get messy
          // (until we switch to using ids)
          (item) =>
            item[f] &&
            item[f].toString().toLowerCase() == val.toString().toLowerCase(),
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
      };

      return data.filter(filterfunc);
    },

    aggregate(data, by, on, flatten = false) {
      /*
         by: array of column specs to aggregate by,
         on: array of column specs to aggregate on,
         flatten: whether to return the data as an array.
                  defaults to false (returns the raw tree).

         a column spec can be either a string (the column name),
         or an object of the form:
         {
           source: 'input_column_name',
           destination: 'output_column_name',
           type: ObjectType, // defaults to Number
         }

         `by` can also take
          - a `final` property, which specifies that the aggregation
            should be done at the leaf level instead.
            only one such column may exist.

         `on` can also take
          - an `exclude` property, which expects boolean values
            (rows are excluded when `exclude` property is true).
          - an `exclude_empty` property, which expects object values
            (rows are excluded when `exclude` property is empty array or object)
       */

      const bycols = {};
      let finalbycol;
      for (const col of by) {
        let src,
          dst,
          final = false;
        if (typeof col == "string") {
          src = dst = col;
        } else {
          src = col.source;
          dst = col.destination;
          final = col.final;

          if (dst === undefined) dst = src;
        }

        if (!src)
          throw new Error(
            "`by` column source not provided: " + JSON.stringify(col),
          );

        if (final) {
          if (finalbycol) throw new Error("Multiple final `by` columns");
          finalbycol = {
            source: src,
            destination: dst,
          };
        } else {
          bycols[src] = dst;
        }
      }
      const _bycols = Object.keys(bycols);

      const oncols = {};
      for (const col of on) {
        let src, dst, type, exclude, exclude_empty;
        if (typeof col == "string") {
          src = dst = col;
          type = Number;
        } else {
          src = col.source;
          dst = col.destination;
          type = col.type;

          if (dst === undefined) dst = src;
          if (type === undefined) type = Number;
        }
        exclude = col.exclude;
        exclude_empty = col.exclude_empty;

        if (!src)
          throw new Error(
            "`on` column source not provided: " + JSON.stringify(col),
          );

        oncols[src] = {
          destination: dst,
          type: type,
          exclude: exclude,
          exclude_empty: exclude_empty,
        };
      }

      // each aggregation level is a sub-dictionary,
      // each aggregation item a key.
      const aggregator = {};

      for (let item of data) {
        item = this.preprocessItem(item);
        const base = {};
        let row = aggregator;
        for (let i = 0, j = _bycols.length; i < j; i++) {
          const srccol = _bycols[i],
            dstcol = bycols[srccol],
            value = item[srccol];

          base[dstcol] = value;

          if (row[value] === undefined) row[value] = i === j - 1 ? base : {};

          row = row[value];
        }

        for (const srccol in oncols) {
          const _col = oncols[srccol],
            dstcol = _col.destination,
            type = _col.type,
            exclude = _col.exclude,
            exclude_empty = _col.exclude_empty;

          let value = type === Number ? Number(item[srccol]) : item[srccol];

          if (value === undefined) continue;
          let current = row[dstcol];

          if (srccol === "beneficiary" && (value === "GR" || value === "EL")) {
            switch (this.period) {
              case "2004-2009":
              case "2009-2014":
                value = "GR";
                break;
              case "2014-2021":
              default:
                value = "EL";
                break;
            }
          }

          if (type === Number) {
            // numbers are added together
            if (current === undefined) current = row[dstcol] = 0;

            if (exclude && item[exclude]) {
              continue;
            }
            if (
              exclude_empty &&
              (item[exclude_empty] === undefined ||
                (typeof item[exclude_empty] == "object" &&
                  Object.keys(item[exclude_empty]).length === 0))
            ) {
              continue;
            }

            row[dstcol] = current + value;
          } else if (type === String || type === Array || type === Object) {
            // strings, arrays items and object keys are consolidated into sets
            if (current === undefined) current = row[dstcol] = new Set();

            if (exclude && item[exclude]) {
              continue;
            }
            if (
              exclude_empty &&
              (item[exclude_empty] === undefined ||
                (typeof item[exclude_empty] == "object" &&
                  Object.keys(item[exclude_empty]).length === 0))
            ) {
              continue;
            }

            if (type === String) {
              current.add(value);
            } else if (type === Array) {
              for (const v of value) {
                current.add(v);
              }
            } else if (type === Object) {
              for (const k in value) {
                current.add(k);
              }
            }
          } else console.warn(srccol, ":: unknown type", type);
        }
      }

      if (!flatten) return aggregator;

      const out = [],
        levels = by.length;

      function recurse(obj, level) {
        if (level === levels) {
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
    preprocessItem(item) {
      return item;
    },
    main() {
      /*
       * main entry point, only called on ready
       */
      // no need to throw, some components could be Vue-only
      //throw "Base.main(): Not implemented";
    },
  },
};
</script>
