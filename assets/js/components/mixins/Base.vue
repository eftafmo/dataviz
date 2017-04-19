<script>
import * as d3 from 'd3';

// site-wide navigation filters
const FILTERS = {
  fm: null,
  state: null,
  sector: null,
};

export default {
  props: {
    datasource: String, // TODO: required?
    initial: Object,
  },

  data() {
    return {
      data: this.initial && this.processData(this.initial) || {},
      filters: FILTERS,
    };
  },

  computed: {
    isReady() {
      return !!(this.data && this.$el);
    },
  },

  created() {
    if (!this.data) this.fetchData();
  },

  mounted() {
    if (this.isReady) this.main();
  },

  methods: {
    main() {
      /*
       * main entry point.
       * implementation make sure this it only gets called when on ready
       */

      throw "Not implemented";
    },

    fetchData() {
      if (!this.datasource) throw "Missing datasource."
      const $this = this;

      d3.json(this.datasource, function(error, data) {
        if (error) throw error;
        $this.data = $this.processData(data);
      });
    },

    processData(data) {
      // override this as needed.
      return data;
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
    'data': {
      handler() {
        if (this.isReady) main();
      },
    },
    'filters.fm': 'handleFilterFm',
    'filters.region': 'handleFilterRegion',
    'filters.sector': 'handleFilterSector',
  },
};
</script>
