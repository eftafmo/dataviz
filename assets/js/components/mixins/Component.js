import * as util from "../../lib/util.js";

const shortCurrency = [
  {
    value: Math.pow(10, 9),
    suffix: "B",
  },
  {
    value: Math.pow(10, 6),
    suffix: "M",
  },
  {
    value: Math.pow(10, 3),
    suffix: "K",
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
        value = value / short.value;
        if (value >= 100 || Number.isInteger(value)) {
          return util.formatCurrency(value) + short.suffix;
        } else {
          return util.formatCurrencyFloat(value) + short.suffix;
        }
      }
      return this.currency(value);
    },
    singularize: util.singularize,
    pluralize: util.pluralize,
  },
};
