<template>
  <div id="sidebar-results" class="sidebar sidebar-results" v-if="hasData">
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

    <div class="sidebar-tabs">
      <nav class="sidebar-tab-menu">
        <a class="sidebar-tab-menu-item"
           v-on:click="selectTab('results')"
           v-bind:class="{ active: (selectedTab == 'results') }">
          <span class="counter">14</span>
          Results
        </a>
        <a class="sidebar-tab-menu-item"
           v-on:click="selectTab('programmes')"
           v-bind:class="{ active: (selectedTab == 'programmes') }">
          <span class="counter">156</span>
          Programmes
        </a>
      </nav>
    </div>

    <div class="sidebar-tab-content">
      <results :datasource="datasource" id="results"
                          v-bind:selected="(selectedTab == 'results')"/>
      <programmes :datasource="datasource" id="programmes"
                          v-bind:selected="(selectedTab == 'programmes')"/>
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
  import Results from './Results';
  import BaseMixin from './mixins/Base';
  import Programmes from './Programmes'

export default Vue.extend({
  mixins: [
    BaseMixin
  ],

  components: {
    results: Results,
    programmes: Programmes
  },

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
    }
  },

  created () {
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
          console.log('expand');
          this.isMobileExpanded = true;
          this.$el.classList.add('is-expanded-on-mobile');
        }
      },

    mobileCollapse(e) {
      e = e || window.event;
      e.stopPropagation(); // event will trigger expand and cancel collapse

      if (this.isMobileExpanded) {
        console.log('collapse');
        this.isMobileExpanded = false;

        var el = this.$el;

        el.classList.remove('is-expanded-on-mobile');
      }
    },

    handleFilter() {
      this.transitioned = !this.transitioned;
    },
  },
});

</script>
