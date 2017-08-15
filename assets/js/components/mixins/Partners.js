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
    this.filter_by.push('DPP');

    // not sure if this is needed
    this.aggregate_on.push({source: 'donor', destination: 'donors', type: String});
    this.aggregate_on.push({source: 'programme', destination: 'programmes', type: String});
  },
};
