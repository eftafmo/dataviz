import * as util from "../../lib/util.js";

export const shortKilo = {
  value: Math.pow(10, 3),
  suffix: "\xa0K",
};
export const shortMillion = {
  value: Math.pow(10, 6),
  suffix: "\xa0m",
};
export const shortBillion = {
  value: Math.pow(10, 9),
  suffix: "\xa0bn",
};
const shortNumberValues = [shortBillion, shortMillion, shortKilo];

function formatShort(
  value,
  formatInteger,
  formatFloat,
  force_short = null,
  decimals = 1
) {
  let suffix = "";
  const short = force_short
    ? force_short
    : shortNumberValues.find((short) => value >= short.value);
  if (short) {
    value = parseFloat((value / short.value).toFixed(decimals));
    suffix = short.suffix;
  }
  if (value >= 100 || Number.isInteger(value)) {
    return formatInteger(value) + suffix;
  } else {
    return formatFloat(value) + suffix;
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
      return formatShort(value, util.formatCurrency, util.formatCurrencyFloat);
    },
    shortCurrencyBF(value) {
      return value >= 1000000
        ? this.shortCurrency(value)
        : formatShort(
            value,
            util.formatCurrency,
            util.formatCurrencyFloat2,
            shortMillion,
            2
          );
    },
    singularize: util.singularize,
    pluralize: util.pluralize,
  },
};
