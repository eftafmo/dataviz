<script>
import Vue from 'vue';
import * as d3 from 'd3';

import FMLegendComponent from '../includes/FMLegend';

import FMs from 'js/constants/financial-mechanisms.json5';
import {FMColours} from 'js/constants';


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
      return this.filters.fm == this.getFmId(fm);
    },
    isDisabled(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm != this.getFmId(fm);
    },

    getFmId(fm) {
      // silly utility func to return FM's id regardless of input type
      let fmid;
      // is this the id already?
      if (typeof fm == "string") fmid = fm;
      else if (typeof fm == "object") {
        // regular fm object?
        if (fm.id !== undefined) fmid = fm.id;
        // a result of d3.entries()?
        else if (fm.key !== undefined) fmid = fm.key;
      }
      return FMs[fmid] ? fmid : null;
    },

    toggleFm(fm, etarget) {
      const fmid = this.getFmId(fm);
      this.filters.fm = this.filters.fm == fmid ?
                         null : fmid;
    },

    triggerclick() {
      var select = event.target;
      var selected_opt= select.options[select.selectedIndex];
      selected_opt.click();
    },

    resetfilter(){
     var reset_element = document.querySelector('option.selected');
     reset_element.click();
    },

    _colour: d3.scaleOrdinal()
      .domain(d3.keys(FMColours))
      .range(d3.values(FMColours)),
    colour(fm) {
      const fmid = this.getFmId(fm);
      if (fmid) return this._colour(this.getFmId(fm));
    },
  },
};
</script>
