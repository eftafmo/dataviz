<template>
    <div  v-if="hasData" class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="transitioned">
          <strong>{{ currency(data.project_count) }} projects</strong>
          <small>{{ currency(data.project_count_positive) }} projects ({{ data.project_percent_positive }} %) have had positive effects that are likely to continue beyond the funding period</small>
        </div>
      </transition>
    </div>
</template>

<style>
.sidebar-header {
  position: relative;
  padding: 0 !important;
}

.allocation {
  padding: 1rem;
  width: 100%;
}

.sidebar-tab-content .active {
  display: block;
}

.allocation.fade-enter-active {
  position: absolute;
  top: 0;
  left: 0;
}

.allocation.fade-enter-active, .allocation.fade-leave-active {
  transition: opacity .5s;
}
.allocation.fade-enter, .allocation.fade-leave-to {
  opacity: 0
}
</style>

<script>
  import Vue from 'vue';
  import BaseMixin from './mixins/Base';

export default Vue.extend({
  mixins: [
    BaseMixin
  ],

  data() {
    return {
      transitioned: false,
    }
  },

  computed: {
    data() {
      const dataset = this.filter(this.dataset);

      const out = {
        project_count: 0,
        project_count_positive: 0,
        project_count_ended: 0,
        project_percent_positive: 0,
      };

      for (const row of dataset) {
        out.project_count += row.project_counts.total;
        out.project_count_positive += row.project_counts.positive_effects;
        out.project_count_ended += row.project_counts.has_ended;
      }

      if (out.project_count_ended) {
        out.project_percent_positive = Math.round(100*out.project_count_positive/out.project_count_ended);
      }

      return out;
    },
  },
  methods: {

    handleFilter() {

      this.transitioned = !this.transitioned;
    },

  },

});

</script>
