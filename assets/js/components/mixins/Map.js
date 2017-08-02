/*
  // ATTENTION: map-base must be used like this:

  <map-base
      ref="base"
      v-on:rendered="baseRendered"
  >

 */

import MapBase from '../includes/MapBase';


export default {
  type: "map",

  components: {
    "map-base": MapBase,
  },

  data() {
    let origin = "";
    if (this.datasource) {
      const host = this.datasource.replace(/^(https?:)?\/\/([^\/]+)\/.*$/, '$2')
      origin = location.protocol +'//' + host;
    }

    return {
      origin: origin,

      width: 0,
      height: 0,

      base_rendered: false,
    };
  },

  mounted() {
    const map = this.map = this.$refs.base;
    this.width = map.width;
    this.height = map.height;
  },

  computed: {
    rendered() {
      return this.base_rendered && this.chart_rendered;
    },

    isReady() {
      return !!(this.hasData
               && this.$el
               && this.base_rendered);
    },
  },

  methods: {
    baseRendered() {
      this.base_rendered = true;
    },

    stateEnter(d) {
      return;
    },

    stateLeave(d) {
      return;
    },

    stateClick(d) {
      return;
    },
  },
};
