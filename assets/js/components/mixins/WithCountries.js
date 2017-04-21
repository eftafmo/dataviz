/*
 * This isn't really a mixin.
 * It just imports all country flags as svg sprites,
 * using webpack's svg-sprite-loader.
 */

import countries from 'js/constants/countries.json5';

function get_flag_name(c) {
  const flag = c.toLowerCase().replace(/ /g, '');
  return `flag-${flag}`;
}

const req = require.context('svg-sprite-loader!imgs', false, /flag-[a-z]+\.png$/);
// we could load all of req.keys() instead, but we want things to fail
// if there's a mismatch between country names and png files.
// (possible TODO: compare req.keys() with countries and warn if necessary)
for (let c of countries) {
  req(`./${get_flag_name(c)}.png`);
}

export {get_flag_name};
