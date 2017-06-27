<template>
    <div  v-if="hasData" class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="transitioned">
          <strong>{{ currency(data.allocation) }}</strong>
          <small>{{ currency(data.bilateral_allocation) }} for bilateral relations</small>
        </div>
      </transition>
    </div>
</template>

<style>
.sidebar-header {
  position: relative;
}

.allocation {
  width: 100%;
}

.sidebar-tab-content .active {
  display: block;
}

.allocation.fade-enter-active {
  position: absolute;
  top: 1rem;
  width: calc(100% - 2rem);
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
      const out = this.aggregate(
        dataset,
        [],
        [
          'allocation',
          'bilateral_allocation',
        ],
        false
      );

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
