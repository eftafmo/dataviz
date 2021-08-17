import { slugify } from "@js/lib/util";
import _SECTORS from "@js/constants/priority-sectors.json5";

const SECTORS = {};
for (const sector of _SECTORS) {
  const sid = slugify(sector.name);
  SECTORS[sid] = Object.assign({ id: sid }, sector);
}

export default {
  beforeCreate() {
    // no point in this being observable
    this.SECTORS = SECTORS;
  },
  data() {
    return {};
  },
  computed: {
    SECTORS_ARRAY() {
      return Object.values(this.SECTORS);
    },
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
    sectorUrl(sectorname) {
      return this.getAssetUrl(
        `sprites/sectors/${this.SECTORS[slugify(sectorname)].icon}`
      );
    },
  },
};
