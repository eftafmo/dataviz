import * as d3 from "d3";

export function color2gray(color, opacity) {
  /*
   * transforms the color to grayscale while applying
   * an optional simulated opacity change
   */
  // computes the gray value as a weighted average.
  // the constants are from the sRGB luminance calculation:
  // https://en.wikipedia.org/wiki/SRGB#The_sRGB_gamut
  const R = 0.2126;
  const G = 0.7152;
  const B = 0.0722;

  const c = d3.rgb(color);
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
  decimal: ".",
  //thousands: "\u00a0", // nbsp
  thousands: ",",
  grouping: [3],
  currency: ["€", ""],
  percent: "%",
};
// currency, separators, float
export const formatCurrencyFloat = d3.formatLocale(_locale).format("$,.1f");
export const formatCurrencyFloat2 = d3.formatLocale(_locale).format("$,.2f");
// currency, separators, int
export const formatCurrency = d3.formatLocale(_locale).format("$,d");
export const formatNumber = d3.formatLocale(_locale).format(",d");
export const formatFloat = d3.formatLocale(_locale).format(",.1f");

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

export function getAssetUrl(path, origin = null) {
  // Convoluted logic here so it works in: debug, prod and embed.
  return new URL(
    `/assets/${path}`,
    origin || (import.meta && import.meta.url) || window.location.origin
  ).href;
}

export function downloadDataUrl(dataUrl, filename) {
  const tempLink = document.createElement("a");
  tempLink.style.display = "none";
  tempLink.href = dataUrl;
  tempLink.setAttribute("download", filename);

  // Safari thinks _blank anchor are pop ups. We only want to set _blank
  // target if the browser does not support the HTML5 download attribute.
  // This allows you to download files in desktop safari if pop up blocking
  // is enabled.
  if (typeof tempLink.download === "undefined") {
    tempLink.setAttribute("target", "_blank");
  }
  document.body.appendChild(tempLink);
  tempLink.click();
  document.body.removeChild(tempLink);
}

export function downloadFile(blob, filename) {
  if (typeof window.navigator.msSaveBlob !== "undefined") {
    // IE workaround for "HTML7007: One or more blob URLs were
    // revoked by closing the blob for which they were created.
    // These URLs will no longer resolve as the data backing
    // the URL has been freed."
    window.navigator.msSaveBlob(blob, filename);
  } else {
    const windowURL = window.URL || window.webkitURL || window;
    const blobURL = windowURL.createObjectURL(blob);
    downloadDataUrl(blobURL, filename);
    windowURL.revokeObjectURL(blobURL);
  }
}

/**
 * Sums start and the items of an iterable from left to right and
 * returns the total.
 *
 * @param values {Number[]}
 * @param start {Number}
 * @return {Number}
 */
export function sum(values, start = 0) {
  return values.reduce((collector, item) => collector + item, start);
}
