import Vue from 'vue';
import * as d3 from 'd3';

import FMLegendComponent from '../includes/FMLegend';
import FMS from 'js/constants/financial-mechanisms.json5';


export default {
  beforeCreate() {
    this.FMS = FMS;
  },

  components: {
    'fm-legend': FMLegendComponent,
  },

  data() {
    return {
      // TODO: get rid of this, and use this.FMS
      fms: FMS,
    };
  },

  methods: {
    fmcolour(fmid) {
      return FMS[fmid].colour;
    },

    getFilterClassFm(fm) {
      if (!this.filters.fm)
        return;

      if (this.isSelectedFm(fm))
        return "selected";

      if (this.isDisabledFm(fm))
        return "disabled";
    },

    isSelectedFm(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm == fm.name;
    },
    isDisabledFm(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm != fm.name;
    },

    toggleFm(fm, etarget) {
      const fmname = fm.name;
      this.filters.fm = this.filters.fm == fmname ?
                        null : fmname;
    },
  },
};
