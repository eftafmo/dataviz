<template>
    <div v-show="hasData" class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="changed">
          <strong>{{ data.DPP_count }} donor programme {{ singularize('partners', data.DPP_count) }}</strong>
          <small> {{ data.dpp_count }} donor project {{ singularize('partners', data.dpp_count) }}</small>
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
      if (!this.hasData) return {}

      const out = this.aggregate(
        this.filtered,
        [],
        [
          {source: "DPP", destination: "DPP", type: String},
          {source: "PJDPP", destination: "dpp", type: Object}
        ],
        false
      );

      // we'll compute these here,
      // so we don't have to use v-if in the template
      out.DPP_count = out.DPP.size()
      out.dpp_count = out.dpp.size()

      return out;
    },
  },
});
</script>
