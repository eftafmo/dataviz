import * as d3 from 'd3';

export function colour2gray(colour, opacity) {
  /*
   * transforms the colour to grayscale while applying
   * an optional simulated opacity change
   */
  // computes the gray value as a weighted average.
  // the constants are from the sRGB luminance calculation:
  // https://en.wikipedia.org/wiki/SRGB#The_sRGB_gamut
  const R = 0.2126, G = 0.7152, B = 0.0722;

  const c = d3.rgb(colour);
  const Y = c.r * R + c.g * G + c.b * B;

  if(opacity === undefined)
    return d3.rgb(Y, Y, Y);

  const x = Y + (255 - Y) * (1 - opacity);
  return d3.rgb(x, x, x);
}

export function slugify(text) {
  return text.toString()
    .toLowerCase()
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
    .replace(/^-+/, '')             // Trim - from start of text
    .replace(/-+$/, '');            // Trim - from end of text
}
