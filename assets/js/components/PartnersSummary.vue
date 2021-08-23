<template>
  <div v-show="hasData" :class="classNames">
    <transition name="fade">
      <div v-if="data.DPP_count > 0" :key="changed" class="allocation">
        <strong
          >{{ data.DPP_count }} Donor Programme
          {{ singularize("partners", data.DPP_count) }}</strong
        >
        <small v-if="data.dpp_count > 0"
          >{{ data.dpp_count }} Donor project
          {{ singularize("partners", data.dpp_count) }}</small
        >
        <small v-if="data.dpp_count == 0">No Donor project partners</small>
      </div>
      <div v-else-if="data.DPP_count == 0" class="allocation">
        <strong>No Donor Programme Partners</strong>
        <small v-if="data.dpp_count > 0">
          {{ data.dpp_count }} donor project
          {{ singularize("partners", data.dpp_count) }}</small
        >
        <small v-if="data.dpp_count == 0">No Donor project partners</small>
      </div>
    </transition>
  </div>
</template>


<script>
import Summary from "./Summary";
import PartnersMixin from "./mixins/Partners";

export default {
  extends: Summary,
  mixins: [PartnersMixin],

  computed: {
    data() {
      if (!this.hasData) return {};

      const out = this.aggregate(
        this.filtered,
        [],
        [
          { source: "DPP", destination: "DPP", type: String },
          { source: "PJDPP", destination: "dpp", type: Object },
        ],
        false
      );

      // we'll compute these here,
      // so we don't have to use v-if in the template
      out.DPP_count = out.DPP ? out.DPP.size : 0;
      out.dpp_count = out.dpp ? out.dpp.size : 0;

      return out;
    },
  },
};
</script>
