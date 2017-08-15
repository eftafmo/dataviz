<template>
    <div v-if="hasData" class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="changed">
          <strong>{{ data.DPP.size() }} donor programme {{ singularize('partners', data.DPP.size()) }}</strong>
          <small> {{ data.dpp.size() }} donor project {{ singularize('partners', data.dpp.size()) }}</small>
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
          {source: "DPP", destination: "DPP", type: String},
          {source: "PJDPP", destination: "dpp", type: Object}
        ],
        false
      );
      return out;
    },
  },
});
</script>
