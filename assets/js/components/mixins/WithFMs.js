import FMLegendComponent from "../includes/FMLegend";
import FMS from "@js/constants/financial-mechanisms.json5";

export default {
  components: {
    "fm-legend": FMLegendComponent,
  },

  computed: {
    // TODO: make the constants arrays, and the objects pre-computed
    FM_ARRAY() {
      return Object.values(this.FMS);
    },
  },

  created() {
    let key = this.period;
    if (!this.period || this.period === "none") {
      key = "2014-2021";
    }
    this.FMS = FMS[key];
  },

  methods: {
    fmcolor(fmid) {
      return this.FMS[fmid].color;
    },

    getFilterClassFm(fm) {
      if (!this.filters.fm) return;

      if (this.isSelectedFm(fm)) return "selected";

      if (this.isDisabledFm(fm)) return "disabled";
    },

    isSelectedFm(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm === fm.name;
    },
    isDisabledFm(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm !== fm.name;
    },

    toggleFm(fm) {
      // don't filter by zero-valued items
      if (fm.value === 0) return;

      const fmname = fm.name;
      this.filters.fm = this.filters.fm === fmname ? null : fmname;
    },
  },
};
