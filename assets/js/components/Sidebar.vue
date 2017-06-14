<template>
  <div class="sidebar">
    <button type="button" id="close-sidebar" class="no-btn"
                  title="Close results"
                v-if="isMobileExpanded"
                v-on:click="mobileCollapse">
          <span class="icon icon-close"></span>
  </button>
    <slot name="Allocation_overview"></slot>
    <slot name="Tabs"></slot>
  </div>
</template>

<style lang="less">
.sidebar {
  #close-sidebar {
    z-index: 1;
  }
}
</style>

<script>
  import Vue from 'vue';

export default Vue.extend({

  data() {
    return {
      onMobile: false,
      isMobileExpanded: false,
    }
  },
  watch: {
    onMobile (matches) {
        if (matches) {
          this.$el.addEventListener('click', this.mobileExpand, false);
        } else {
          this.$el.removeEventListener('click', this.mobileExpand, false);
          this.mobileCollapse();
        }
  },
},
  updated () {
    // Add a media query listener handle mobile events
    var mq = window.matchMedia ('(max-width: 768px)');
    var self = this;
    mq.addListener(function(mq) { self.onMobile = mq.matches; });
    this.onMobile = mq.matches; // initial check;
  },
  methods: {
      mobileExpand() {
        if (!this.isMobileExpanded) {
          this.isMobileExpanded = true;
          this.$el.classList.add('is-expanded-on-mobile');
        }
      },
    mobileCollapse(e) {
      e = e || window.event;
      e.stopPropagation(); // event will trigger expand and cancel collapse
      if (this.isMobileExpanded) {
        this.isMobileExpanded = false;
        var el = this.$el;
        el.classList.remove('is-expanded-on-mobile');
      }
    },
  },
});
</script>
