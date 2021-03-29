<template>
<fms :datasource="datasource" :initial="initial">
  <template slot="title"><slot name="title"></slot></template>
  <template slot="legend" slot-scope="x">
    <fm-legend :fms="x.data"></fm-legend>
  </template>
</fms>
</template>


<style lang="less">
.dataviz .viz.fms.is-partners {
  .legend {
    .fms{
      text-align: left;
    }
    .fm {
      border: none;
      padding-right: 0;
      margin-right: 0;
      min-width: initial;
      span.fill {
        vertical-align: middle;
        width: 1.4em;
        height: 1.4em;
        margin-right: 0.2em;
      }
    }
  }
}
</style>


<script>
import Component from './Component';
import BaseMechanisms from './Mechanisms';

import PartnersMixin from './mixins/Partners';
import FMLegendComponent from './includes/FMLegend';


const Mechanisms = BaseMechanisms.extend({
  mixins: [
    PartnersMixin,
  ],

  data() {
    return {
    };
  },

  computed: {
    aggregated() {
      // allocation amounts are duplicated sometimes by donors,
      // so we need to overwrite it.
      this.aggregate_on = this.aggregate_on.filter(item => item !== 'allocation');
      const aggregated = this.aggregate(this.filtered,
                                        this.aggregate_by,
                                        this.aggregate_on);
      for (const k in aggregated) {
        aggregated[k].allocation = 0;
      }
      const keys = new Set();
      const dataset = this.filtered;
      for (let d of dataset) {
        const key = d.programme + d.beneficiary + d.area;
        if (!keys.has(key)) {
          keys.add(key);
          aggregated[d.fm].allocation += d.allocation;
        }
      }
      return aggregated;
    },
  },

  methods: {
    tooltipTemplate(d) {
      return `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <ul>
          <li>${d.programmes.size()} partner ` + this.singularize(`programmes`, d.programmes.size()) + `</li>
          <li>${d.beneficiaries.size()} `+  this.singularize(`beneficiary states`, d.beneficiaries.size()) + `</li>
          <li>${d.sectors.size()} `+  this.singularize(`sectors`, d.sectors.size()) + `</li>
          <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
      `;
    },
  },
});


export default Component.extend({
  components: {
    fms: Mechanisms,
    'fm-legend': FMLegendComponent,
  },
});
</script>
