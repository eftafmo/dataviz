<template>
  <div id="sidebar-results" class="sidebar sidebar-results">
    <div class="sidebar-header">
      <strong>{{format(dataset.Total)}}</strong>
      <small>{{format(dataset.Bilateral)}} for bilateral relations</small>
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
      <sidebar_results_tab :initial="results" id="results"
                          v-bind:selected="(selectedTab == 'results')"/>
    <!--   <sidebar-result-tab id="programmes"
                          v-bind:selected="(selectedTab == 'programmes')"/> -->
    </div>
  </div>
</template>

<style>

</style>

<script>
  import Vue from 'vue';
  import Results from './SidebarResultTab';
  import results_data from 'js/dummy.js';
  import BaseMixin from './mixins/Base';


export default Vue.extend({
  mixins: [
    BaseMixin
  ],

  components: {
    'sidebar_results_tab': Results,
  },


  data() {
      return {
        results: results_data,
        message: "Am triumfat",
        onMobile: false,
        isMobileExpanded: false,
        selectedTab: undefined
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
      }
    }

  });

</script>
