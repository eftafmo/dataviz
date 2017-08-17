import * as util from '../../lib/util.js'

export default {
  data() {
    return {
      // opacity of filtered-out items
      inactive_opacity: .7,
    }
  },

  computed: {
    currency() {
      return util.formatCurrency
    },

    number() {
      return util.formatNumber
    },

    inactivecolour() {
      return (
        (c) => util.colour2gray(c, this.inactive_opacity)
      )
    },

    singularize() {
      return util.singularize
    },

    pluralize() {
      return util.pluralize
    },
  },
}
