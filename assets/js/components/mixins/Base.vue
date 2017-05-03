<script>
import * as d3 from 'd3';
import {FILTERS} from '../../globals.js'

export default {
  props: {
    datasource: String, // TODO: required?
    initial: Object,
  },

  data() {
    return {
      dataset: (this.initial
                && this.processDataset(this.initial)
                || undefined),
      filters: FILTERS,
    };
  },

  computed: {
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
    if (!this.hasData) this.fetchData();
  },

  mounted() {
    if (this.isReady) this.main();
  },

  methods: {
    main() {
      /*
       * main entry point.
       * implementations need to make sure this only gets called on ready
       */

      throw "Not implemented";
    },

    fetchData() {
      if (!this.datasource) throw "Missing datasource."

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
      //throw "Unhandled filter: " + type;
      console.log(`» [${type}] filter:`, old,'→', val);
    },
    handleFilterFm(val, old) {
      const type = "fm";
      this.handleFilter(type, val, old);
    },
    handleFilterRegion(val, old) {
      const type = "region";
      this.handleFilter(type, val, old);
    },
    handleFilterSector(val, old) {
      const type = "sector";
      this.handleFilter(type, val, old);
    },

    /*
     * utility methods available to all instances,
     * be they charts or not.
     */
    format: d3.formatLocale({
      // see https://github.com/d3/d3-format/blob/master/locale/
      // TODO: derive and extend the browser locale?
      // useful characters: nbsp: "\u00a0", narrow nbsp: "\u202f"
      "decimal": ",", // that's the european way
      "thousands": ".", // dot, the european way
      "grouping": [3],
      "currency": ["€", ""],
      "percent": "%",
    }).format("$,d"), // currency; thousand separators; decimal int.
  },
  watch: {
    'dataset': {
      handler() {
        if (this.isReady) this.main();
      },
    },
    // make sure every key exists from the start
    'filters.fm': 'handleFilterFm',
    'filters.region': 'handleFilterRegion',
    'filters.sector': 'handleFilterSector',
  },
};
</script>
