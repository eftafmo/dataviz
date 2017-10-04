/*
  // ATTENTION: map-base must be used like this:

  <map-base
      ref="map"
      v-on:rendered="handleMapRendered"
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
               && this.is_mounted
               && this.map_rendered)
    },
  },

  methods: {
    getRegionLevel(id) {
      if (!id) return null
      return id.length - 2
    },

    // ancestor id, descendant id
    isAncestorRegion(aid, did) {
      return aid == did.substr(0, aid.length)
    },

    getAncestorRegion(id, lvl) {
      return id.substr(0, 2 + lvl)
    },

    handleMapRendered() {
      this.map_rendered = true
    },
  },
};
