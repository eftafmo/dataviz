import {slugify} from 'js/lib/util';
import _SECTORS from 'js/constants/priority-sectors.json5';

const SECTORS = {};
for (const sector of _SECTORS) {
  const sid = slugify(sector.name)
  SECTORS[sid] = Object.assign({id: sid}, sector);
}

const req = require.context('svg-sprite-loader!imgs/sectors', false, /[a-z]+\.png$/);
// we could load all of req.keys() instead, but we want things to fail
// if there's a mismatch between country names and png files.
// (possible TODO: compare req.keys() with countries and warn if necessary)
for (const code in SECTORS) {
  req(`./${code}.png`);
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
  },
};
