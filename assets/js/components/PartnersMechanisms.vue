<template>
<fms :datasource="datasource" :initial="initial" class="partners">
  <template slot="legend" scope="x">
    <fm-legend :fms="x.data"></fm-legend>
  </template>
</fms>
</template>


<style lang="less">
.fms-viz.partners {
  .legend {
    .fm {
      border: none;

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
import Vue from 'vue';

import BaseMechanisms from './Mechanisms';
import PartnersMixin from './mixins/Partners';
import ComponentMixin from './mixins/Component.vue';
import FMLegendComponent from './includes/FMLegend';


const Mechanisms = BaseMechanisms.extend({
  mixins: [PartnersMixin],

  computed: {
    aggregated() {
      // allocation amounts are multiplied by the number of donors,
      // so we need to fumble with the data a bit.
      const aggregated = this.aggregate(this.filtered,
                                        this.aggregate_by,
                                        this.aggregate_on);

      for (const k in aggregated) {
        const item = aggregated[k];
        // TODO: division by zero ever possible?
        item.allocation = item.allocation / item.donor_states.size();
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
          <li>${d.partnership_programmes.size()} partner programmes</li>
<!--
          <li>Donors: ${d.donor_states.values().join(", ")}</li>
          <li>${this.currency(d.allocation)} gross allocation</li>
-->
          <li>${d.beneficiaries.size()} `+  this.singularize(`beneficiary states`, d.beneficiaries.size()) + `</li>
          <li>${d.sectors.size()} `+  this.singularize(`sectors`, d.sectors.size()) + `</li>
          <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
      `;
    },
  },
});


export default Vue.extend({
  mixins: [
    ComponentMixin,
  ],

  components: {
    fms: Mechanisms,
    'fm-legend': FMLegendComponent,
  },
});
</script>
