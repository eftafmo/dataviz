<template>
<div v-if="hasData">
    <div class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="transitioned">
          <strong>{{ format(data.allocation) }}</strong>
          <small>{{ format(data.bilateral_allocation) }} for bilateral relations</small>
        </div>
      </transition>
      <button type="button" id="close-sidebar-results" class="no-btn"
              title="Close results"
              v-if="isMobileExpanded"
              v-on:click="mobileCollapse">
        <span class="icon icon-close"></span>
      </button>
    </div>
    </div>
  </div>
</template>

<style>
sidebar-header {
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
  top: 11px;
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
      // helper for transitioning value changes
      transitioned: false,

      onMobile: false,
      isMobileExpanded: false,
      // select first tab by default
      selectedTab: 'results',
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
    selectTab(tab) {
      this.selectedTab = tab;
    },

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
