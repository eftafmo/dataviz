<template>
  <div id="sidebar-results" class="sidebar sidebar-results">
    <div class="sidebar-header">
      Header
      <button type="button" id="close-sidebar-results" class="no-btn"
              title="Close results"
              v-if="isMobileExpanded"
              v-on:click="mobileCollapse">
        <span class="icon icon-close"></span>
      </button>
    </div>

    <div class="sidebar-tabs">
      <nav class="sidebar-tab-menu">
        <a class="sidebar-tab-menu-item active">
          Results
          <span class="counter">14</span>
        </a>
        <a class="sidebar-tab-menu-item">
          Programmes
          <span class="counter">156</span>
        </a>
      </nav>
    </div>

    <div class="sidebar-tab-content">
      <div class="sidebar-tab-pane active">
        <ul class="no-list">
          <li>
            Some result
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style>

</style>

<script>
  import Vue from 'vue';

  var SidebarResults = Vue.extend({

    data() {
      return {

        message: "Am triumfat",
        onMobile: false,
        isMobileExpanded: false
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

  export default SidebarResults;
</script>
