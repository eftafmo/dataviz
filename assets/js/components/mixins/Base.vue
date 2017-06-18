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

      // unless overriden, displayed values are formatted as currency
      showsCurrency: true,

      // this is only used internally. mind the creative use of unicode,
      // because properties beginning with underscore aren't reactive
      ˉdataset: null,
    };

  },

  computed: {
    dataset: {
      // make dataset a settable computed
      get() {
        return this.ˉdataset || this.initial;
      },
      set(val) {
        this.ˉdataset = val;
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

    format() {
      const locale = {
        // see https://github.com/d3/d3-format/blob/master/locale/
        // TODO: derive and extend the browser locale?
        // useful characters: nbsp: "\u00a0", narrow nbsp: "\u202f"
        "decimal": ",", // that's the european way
        "thousands": ".", // dot, the european way
        "grouping": [3],
        "currency": ["€", ""],
        "percent": "%",
      };

      // show currency. thousand separators. decimal int.
      const format = this.showsCurrency ? "$,d" : "d";

      return d3.formatLocale(locale).format(format);
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
  },
};
</script>
