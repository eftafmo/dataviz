import * as util from "../../lib/util.js";

const shortCurrency = [
  {
    value: Math.pow(10, 9),
    suffix: "B",
  },
  {
    value: Math.pow(10, 6),
    suffix: "m",
  },
  {
    value: Math.pow(10, 3),
    suffix: "k",
  },
];

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
    shortCurrency(value) {
      const short = shortCurrency.find((short) => value >= short.value);
      if (short) {
        // TODO: How do we want to round these numbers?
        return this.currency(Math.round(value / short.value)) + short.suffix;
      }
      return this.currency(value);
    },
    singularize: util.singularize,
    pluralize: util.pluralize,
  },
};
