import * as d3 from "d3";

export function colour2gray(colour, opacity) {
  /*
   * transforms the colour to grayscale while applying
   * an optional simulated opacity change
   */
  // computes the gray value as a weighted average.
  // the constants are from the sRGB luminance calculation:
  // https://en.wikipedia.org/wiki/SRGB#The_sRGB_gamut
  const R = 0.2126;
  const G = 0.7152;
  const B = 0.0722;

  const c = d3.rgb(colour);
  const Y = c.r * R + c.g * G + c.b * B;

  if (opacity === undefined) return d3.rgb(Y, Y, Y);

  const x = Y + (255 - Y) * (1 - opacity);
  return d3.rgb(x, x, x);
}

export function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .replace(/\s+/g, "-") // Replace spaces with -
    .replace(/[^\w-]+/g, "") // Remove all non-word chars
    .replace(/--+/g, "-") // Replace multiple - with single -
    .replace(/^-+/, "") // Trim - from start of text
    .replace(/-+$/, ""); // Trim - from end of text
}

export function truncate(text, max) {
  return text.substr(0, max - 1) + (text.length > max ? "\u2026" : "");
}

const _locale = {
  // see https://github.com/d3/d3-format/blob/master/locale/
  // TODO: derive and extend the browser locale?
  // useful characters: nbsp: "\u00a0", narrow nbsp: "\u202f"
  decimal: ",", // that's the european way
  thousands: "\u00a0", // nbsp
  grouping: [3],
  currency: ["€", ""],
  percent: "%",
};
// currency, separators, float
export const formatCurrencyFloat = d3.formatLocale(_locale).format("$,.1f");
// currency, separators, int
export const formatCurrency = d3.formatLocale(_locale).format("$,d");
export const formatNumber = d3.formatLocale(_locale).format(",d");

export function singularize(str, value) {
  // this works only for supposed plural strings ending in "s" or "ies"
  if (value !== 1) return str;

  let ending = str.substr(-3);
  if (ending === "ies") return str.substr(0, str.length - 3) + "y";

  ending = str.substr(-1);
  if (ending === "s") return str.substr(0, str.length - 1);

  return str;
}

export function pluralize(str, value, suffix) {
  if (value === 1) return str;

  if (typeof suffix === "undefined") suffix = "s";

  return str + suffix;
}
