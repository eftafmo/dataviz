import * as util from "../../lib/util.js";

export default {
  data() {
    return {
      // opacity of filtered-out items
      inactive_opacity: 0.7,
    };
  },

  computed: {
    inactivecolour() {
      return (c) => util.colour2gray(c, this.inactive_opacity);
    },
  },

  methods: {
    currency: util.formatCurrency,
    number: util.formatNumber,

    singularize: util.singularize,
    pluralize: util.pluralize,
  },
};
