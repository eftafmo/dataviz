import {rgb} from 'd3';

export default {
  type: "is-partners",

  data() {
    return {
      colours: {
        programmes: '#089900',
        projects: '#e68a00',
      },
      weak_colours: {
        programmes: rgb(8, 153, 0, 0.2),
        projects: rgb(230, 138, 0, 0.1),
      },
    };
  },

  created() {
    this.filter_by.push('donor');
    this.filter_by.push('DPP');

    // not sure if this is needed
    this.aggregate_on.push({source: 'donor', destination: 'donors', type: String});
    //this.aggregate_on.push({source: 'programme', destination: 'programmes', type: String});
    this.aggregate_on.push({source: 'programmes', destination: 'programmes', type: Object});
  },
};
