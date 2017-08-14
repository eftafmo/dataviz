export default {
  type: "partners",

  data() {
    return {
      colours: {
        programmes: '#30b729',
        projects: '#fea500',
      },
    };
  },

  created() {
    this.filter_by.push('donor');

    // not sure if this is needed
    for (const colspec of [
      {source: 'donor', destination: 'donors', type: String},
      {source: 'partnership_programmes', type: Object},
    ]) {
      this.aggregate_on.push(colspec);
    }
  },
};
