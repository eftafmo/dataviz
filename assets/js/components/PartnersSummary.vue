<template>
    <div v-if="hasData" class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="changed">
          <strong>{{ data.DPP.size() }} donor programme partners</strong>
          <small> {{ data.dpp.size() }} donor project partners</small>
        </div>
      </transition>
    </div>
</template>

<script>
import Summary from './Summary';
import PartnersMixin from './mixins/Partners';


export default Summary.extend({
  mixins: [PartnersMixin],

  computed: {
    data() {
      const out = this.aggregate(
        this.filtered,
        [],
        [
          {source: "donor_programme_partners", destination: "DPP", type: Object},
          {source: "donor_project_partners", destination: "dpp", type: Object}
        ],
        false
      );
      return out;
    },
  },
});
</script>
