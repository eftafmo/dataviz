import NUTS from 'js/constants/nuts.json';


export function getRegionLabel(id) {
  return NUTS[id]
}


export default {
  methods: {
    getRegionLabel,

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
  },
}
