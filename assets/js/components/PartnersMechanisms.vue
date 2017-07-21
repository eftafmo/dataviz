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
import BaseMixin from './mixins/Base';
import FMLegendComponent from './includes/FMLegend';


const Mechanisms = BaseMechanisms.extend({
  mixins: [PartnersMixin],

  created() {
    this.aggregate_by.push('donor_state');
  },

  computed: {
    aggregated() {
      const aggregated = this.aggregate(this.filtered,
                                        this.aggregate_by,
                                        this.aggregate_on);

      const out = {};

      for (const fm in aggregated) {
        // data is duplicated for each donor state
        const item = out[fm] = {
          // TODO: "donors" is taken by constants. fix.
          donor_states: [],
        };

        let itemdata;
        for (const donor in aggregated[fm]) {
          item.donor_states.push(donor);
          itemdata = aggregated[fm][donor];
        }

        delete itemdata['donor_state'];
        Object.assign(item, itemdata);
      }

      return out;
    },
  },

  methods: {
    tooltipTemplate(d) {
      return `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <ul>
          <li>Donor states: ${d.donor_states.join(", ")}</li>
          <li>${this.currency(d.allocation)} gross allocation</li>
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
    BaseMixin,
  ],

  components: {
    fms: Mechanisms,
    'fm-legend': FMLegendComponent,
  },
});
</script>
