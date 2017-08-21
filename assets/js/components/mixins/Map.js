/*
  // ATTENTION: map-base must be used like this:

  <map-base
      ref="map"
      v-on:rendered="mapRendered"
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

      map_rendered: false,
    };
  },

  mounted() {
    const map = this.map = this.$refs.map;
    this.width = map.width;
    this.height = map.height;
  },

  computed: {
    rendered() {
      return this.map_rendered && this.chart_rendered;
    },

    isReady() {
      return !!(this.hasData
               && this.$el
               && this.map_rendered);
    },
  },

  methods: {
    mapRendered() {
      this.map_rendered = true;
    },
  },
};
