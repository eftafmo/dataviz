export default {
  type: "is-projects",

  created() {
    // append projects & programmes to aggregation columns
    this.aggregate_on.push("project_count");
    this.aggregate_on.push("project_allocation");
    this.aggregate_on.push({
      source: "programmes",
      destination: "programmes",
      type: Object,
      exclude: "is_ta",
    });
  },
};
