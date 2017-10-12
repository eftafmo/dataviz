import {slugify} from 'js/lib/util';
import _SECTORS from 'js/constants/priority-sectors.json5';

const SECTORS = {};
for (const sector of _SECTORS) {
  const sid = slugify(sector.name)
  SECTORS[sid] = Object.assign({id: sid}, sector);
}

const req = require.context('svg-sprite-loader!imgs/sectors', false, /[a-z]+\.png$/);
// we could load all of req.keys() instead, but we want things to fail
// if there's a mismatch between sector names and png files.
// (possible TODO: compare req.keys() with sectors and warn if necessary)
for (const sector in SECTORS) {
  req(`./${SECTORS[sector].icon}`);
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
    sectoricon(sectorname) {
      // TODO: mismatch between sectors.icon and slugify(sname)
      // see other.png
      return slugify(sectorname);
    },
  },
};
