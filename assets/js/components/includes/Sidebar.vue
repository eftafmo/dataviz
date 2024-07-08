<template>
  <div class="sidebar" @click="mobileExpand">
    <button
      v-if="isMobileExpanded"
      id="close-sidebar"
      type="button"
      class="no-btn"
      title="Close results"
      @click="mobileCollapse"
    >
      <span class="icon icon-cross"></span>
    </button>
    <slot></slot>
  </div>
</template>

<script>
export default {
  props: {
    embedded: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      // these are only used on the local site
      onMobile: false,
      isMobileExpanded: false,
    };
  },

  watch: {
    onMobile(matches) {
      if (this.embedded) return;
      if (!matches) this.mobileCollapse();
    },
  },

  created() {
    if (this.embedded) return;

    // Add a media query listener handle mobile events
    var mq = window.matchMedia("(max-width: 768px)");
    var self = this;
    mq.addListener(function (mq) {
      self.onMobile = mq.matches;
    });
    this.onMobile = mq.matches; // initial check;
  },

  methods: {
    mobileExpand() {
      if (this.embedded || !this.onMobile) return;

      if (!this.isMobileExpanded) {
        this.isMobileExpanded = true;
        this.$el.classList.add("is-expanded-on-mobile");
        document.querySelector("body").classList.add("sidebar-open");
        document.querySelector("html").classList.add("sidebar-open");
      }
    },

    mobileCollapse(e) {
      if (this.embedded) return;

      e = e || window.event;
      if (e) e.stopPropagation(); // event will trigger expand and cancel collapse
      if (this.isMobileExpanded) {
        this.isMobileExpanded = false;
        var el = this.$el;
        el.classList.remove("is-expanded-on-mobile");
        document.querySelector("body").classList.remove("sidebar-open");
        document.querySelector("html").classList.remove("sidebar-open");
      }
    },
  },
};
</script>

<style lang="less">
@import "@css/style";

.dataviz .sidebar {
  border: 1px solid #ddd;
  background: @bg_color;

  /* Sidebar results Tabs */
  .sidebar-tabs {
    position: relative;
  }

  .is-loading .sidebar-tabs::after {
    content: ""; /* loading spinner */
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: rgba(100, 100, 100, 0.8);
  }
  .tabs-component-tabs {
    border-bottom: 1px solid #ddd;
    position: relative;
    padding-left: 0;
    margin: 0;
    -js-display: flex;
    display: flex;
  }
  .sidebar-tab-menu::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 0.6667em;
    bottom: 0.6667em;
    border-left: 1px solid #ddd;
  }
  .sidebar-tab-menu::after {
    content: "";
    display: block;
    clear: both;
  }
  .tabs-component-tab {
    box-sizing: border-box;
    display: inline-block;
    width: 50%;
    text-align: center;
    position: relative;
    color: #898989;
    cursor: pointer;
    background: transparent;
  }

  .tabs-component-tab a {
    display: block;
    line-height: 3;
    text-decoration: none;
    color: #777777;
  }

  .tabs-component-tab::after {
    content: "";
    display: block;
    position: absolute;
    bottom: -1px;
    left: 1em;
    right: 1em;
    height: 3px;
    background: transparent;
  }
  @media (min-width: 768px) {
    .tabs-component-tab:hover a {
      text-decoration: none;
      color: #3b5998;
    }
    .tabs-component-tab:hover::after {
      background: #3b5998;
    }
  }
  .tabs-component-tab.is-active a {
    color: #3b5998;
    font-weight: 600;
  }
  .tabs-component-tab.is-active::after {
    background: #3b5998;
  }

  /* Sidebar tab pane */
  .sidebar-content {
    position: relative;
    overflow: auto;
    padding: 1.5rem !important;
  }

  .sidebar-content {
    list-style: none;
    padding-left: 0;
    margin: 0 0 1rem;
    overflow: auto;
    max-height: calc(100vh - 40rem);
  }

  .content-item .title {
    margin: 0 0.5rem 0 0;
    flex-shrink: 0;
    font-size: 1.4rem;
    font-weight: inherit;
    color: #000000;
  }

  .content-item {
    margin-top: 2rem;
  }

  .sidebar-content li:first-of-type .content-item {
    margin-top: 0;
  }

  /* Sidebar close */
  #close-sidebar {
    position: absolute;
    z-index: 1;
    top: 0.5rem;
    right: 0.5rem;
    font-size: 2rem;
    color: #898989;

    .icon {
      font-size: 1rem;
      margin-right: 5px;
    }
  }

  &:not(.embedded) {
    @media (max-width: 768px) {
      position: fixed;
      bottom: 1rem;
      right: 1rem;
      z-index: 200;

      width: 220px;
      /*min-width: 200px;*/
      transition:
        width 0.3s,
        height 0.3s;
      overflow: hidden;
      height: 10rem;

      &.is-expanded-on-mobile {
        height: 100%;
        width: 100%;
        bottom: 0;
        right: 0;
        border: none;
      }

      .tabs-component-tab {
        font-size: 1.2rem;
      }

      .tabs-component-tab .counter {
        display: block;
        font-size: 1.5rem;
        font-weight: bold;
      }

      /*Iphone 5 stuff*/
      .tabs-component {
        height: ~"calc(100% - 70px)";
      }

      .tabs-component-panels {
        height: ~"calc(100% - 37px)";
      }

      .tabs-component-panel {
        max-height: 100%;
        overflow: auto;
      }

      .sidebar-content {
        max-height: initial;
        overflow: auto;
      }

      .sidebar-content > div {
        max-height: 100%;
        overflow: auto;
      }
    }

    @media (min-width: 769px) {
      position: sticky;
      margin-top: 2rem;
      top: 40px;
      width: 320px;

      .tabs-component-tab .counter {
        display: none;
      }

      #close-sidebar {
        display: none;
      }
    }
    @media (min-width: 769px) and (max-width: 1000px) {
      width: auto;
    }
  }
}

// this style is to be applied on body. meh.
.sidebar-open {
  overflow: hidden;
  height: 100%;
  position: fixed;
}

// Put the sidebar while the menu is opened on mobile.
.dataviz.menu-is-open .sidebar {
  z-index: 10;
}
</style>
