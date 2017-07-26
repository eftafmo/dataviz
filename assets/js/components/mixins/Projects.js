export default {
  data() {
    return {
    };
  },

  created() {
    // append projects to aggregation columns
    this.aggregate_on.push('project_count');
  },
};
