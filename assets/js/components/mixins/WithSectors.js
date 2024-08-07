import { slugify } from "@js/lib/util";
import _SECTORS from "@js/constants/priority-sectors.json5";

const sectorImages = import.meta.glob("../../../sprites/sectors/*.png", {
  eager: true,
});

const SECTORS = {};
_SECTORS.forEach((sector, index) => {
  const sid = slugify(sector.name);
  SECTORS[sid] = {
    id: sid,
    sortOrder: index,
    img: sectorImages[`../../../sprites/sectors/${sector.icon}`].default,
    ...sector,
  };
});

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
    sectorcolor(sectorname) {
      // using sector's name because we're mostly dealing with that
      return this.SECTORS[slugify(sectorname)].color;
    },
    sectoricon(sectorname) {
      // TODO: mismatch between sectors.icon and slugify(sname)
      // see other.png
      return slugify(sectorname);
    },
    sectorUrl(sectorname) {
      return this.getAssetUrl(
        `sprites/sectors/${this.SECTORS[slugify(sectorname)].icon}`,
      );
    },
    sectorImage(sectorname) {
      return this.SECTORS[slugify(sectorname)].img;
    },
  },
};
