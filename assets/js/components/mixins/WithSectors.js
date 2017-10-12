import {slugify} from 'js/lib/util';
import _SECTORS from 'js/constants/priority-sectors.json5';

const SECTORS = {};
for (const sector of _SECTORS) {
  const sid = slugify(sector.name)
  SECTORS[sid] = Object.assign({id: sid}, sector);
}

// force-load all sector icons so they get bundled as sprites
for (const sector in SECTORS) {
  require(`sprites/sectors/${SECTORS[sector].icon}`)
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
