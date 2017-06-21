import {slugify} from 'js/lib/util';
import _SECTORS from 'js/constants/priority-sectors.json5';

const SECTORS = {};

for (const sector of _SECTORS) {
  const sid = slugify(sector.name)
  SECTORS[sid] = Object.assign({id: sid}, sector);
}

export function get_image(name) {
  const sid = slugify(name),
        sector = SECTORS[sid];
  if (!sector) throw "sector not found: " + name;
  return sid;
}

const req = require.context('svg-sprite-loader!imgs/psIcons', false, /[a-z]+\.png$/);
// we could load all of req.keys() instead, but we want things to fail
// if there's a mismatch between country names and png files.
// (possible TODO: compare req.keys() with countries and warn if necessary)
for (const code in SECTORS) {
  req(`./${get_image(code)}.png`);
}


export default {
  beforeCreate() {
    // no point in this being observable
    this.SECTORS = SECTORS;
  },

  data() {
    return {
    };
  },

  methods: {
    sectorcolour(sectorname) {
      // using sector's name because we're mostly dealing with that
      return this.SECTORS[slugify(sectorname)].colour;
    },
    get_image(c) { return get_image(c) },
  },
};
