<template>
    <div  v-if="hasData" class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="transitioned">
          <strong>{{ format(data.allocation) }}</strong>
          <small>{{ format(data.bilateral_allocation) }} for bilateral relations</small>
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
        allocation: 0,
        bilateral_allocation: 0,
      };

      for (const row of dataset) {
        out.allocation += +row.allocation;
        out.bilateral_allocation += +row.bilateral_allocation;
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
