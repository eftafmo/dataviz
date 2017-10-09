const LOCALFILTERS = {
  region: null
}


export default {
  type: "is-projects",

  data() {
    return {
      localfilters: LOCALFILTERS,
    }
  },

  created() {
    // append projects & programmes to aggregation columns
    this.aggregate_on.push('project_count');
    this.aggregate_on.push(
      {source: "programmes", destination: "programmes", type: Object, exclude: "is_ta"}
    );
  },

  methods: {
    handleFilterRegion(val, old) {
      const type = "region"
      this.handleFilter(type, val, old)
    },
  },

  watch: {
    'localfilters.region': 'handleFilterRegion',
  },
};
