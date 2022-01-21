import * as util from "../../lib/util.js";

const shortNumberValues = [
  {
    value: Math.pow(10, 9),
    suffix: "\xa0bn",
  },
  {
    value: Math.pow(10, 6),
    suffix: "\xa0m",
  },
  {
    value: Math.pow(10, 3),
    suffix: "\xa0K",
  },
];

function formatShort(value, formatInteger, formatFloat) {
  let suffix = "";
  const short = shortNumberValues.find((short) => value >= short.value);
  if (short) {
    value = parseFloat((value / short.value).toFixed(1));
    suffix = short.suffix;
  }
  if (value >= 100 || Number.isInteger(value)) {
    return formatInteger(value) + suffix;
  } else {
    if (suffix) {
      return formatFloat(value) + suffix;
    } else {
      return formatFloat(value) + "\xa0m";
    }
  }
}

export default {
  data() {
    return {
      // opacity of filtered-out items
      inactive_opacity: 0.7,
    };
  },

  computed: {
    inactivecolor() {
      return (c) => util.color2gray(c, this.inactive_opacity);
    },
  },

  methods: {
    currency: util.formatCurrency,
    number: util.formatNumber,
    formatPercent(value, total, fractionDigits = 0) {
      const result = (Number(value) / Number(total)) * 100;
      if (isNaN(result)) return "-";

      return result.toFixed(fractionDigits) + "%";
    },
    shortNumber(value) {
      return formatShort(value, util.formatNumber, util.formatFloat);
    },
    shortCurrency(value) {
      if (value < 1) {
        return formatShort(
          value,
          util.formatCurrency,
          util.formatCurrencyFloatUnderOne
        );
      } else {
        return formatShort(
          value,
          util.formatCurrency,
          util.formatCurrencyFloat
        );
      }
    },
    singularize: util.singularize,
    pluralize: util.pluralize,
  },
};
