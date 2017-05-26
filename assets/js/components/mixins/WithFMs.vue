<script>
import Vue from 'vue';
import * as d3 from 'd3';

import FMLegendComponent from '../includes/FMLegend';

import FMs from 'js/constants/financial-mechanisms.json5';


export default {
  components: {
    'fm-legend': FMLegendComponent,
  },

  data() {
    return {
      fms: FMs,
    };
  },

  methods: {
    getFilterClass(fm) {
      if (!this.filters.fm)
        return;

      if (this.isSelected(fm))
        return "selected";

      if (this.isDisabled(fm))
        return "disabled";
    },

    isSelected(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm == fm.name;
    },
    isDisabled(fm) {
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
</script>
