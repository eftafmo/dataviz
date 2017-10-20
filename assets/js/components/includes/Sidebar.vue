<template>
  <div class="sidebar">
    <button type="button" id="close-sidebar" class="no-btn"
                  title="Close results"
                v-if="isMobileExpanded"
                v-on:click="mobileCollapse">
          <span class="icon icon-cross"></span>
  </button>
    <slot></slot>
  </div>
</template>


<style lang="less">
.dataviz .sidebar {
  border: 1px solid #ddd;
  box-shadow: 0 1px 5px rgba(0,0,0,.2);
  background: #fff;

  /* Sidebar results Tabs */
  .sidebar-tabs {
    position: relative;
  }

  .is-loading .sidebar-tabs::after {
    content: ''; /* loading spinner */
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: rgba(100, 100, 100, .8);
  }
  .tabs-component-tabs{
    border-bottom: 1px solid #ddd;
    position: relative;
    padding-left: 0;
    margin: 0;
    -js-display: flex;
    display: flex;
  }
  .sidebar-tab-menu::before {
    content: '';
    position: absolute;
    left: 50%;
    top: .6667em;
    bottom: .6667em;
    border-left: 1px solid #ddd;
  }
  .sidebar-tab-menu::after {
    content: '';
    display: block;
    clear: both;
  }
  .tabs-component-tab{
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
  }

  .tabs-component-tab::after {
    content: '';
    display: block;
    position: absolute;
    bottom: -1px;
    left: 1em;
    right: 1em;
    height: 3px;
    background: transparent;
  }
  @media (min-width: 768px){
    .tabs-component-tab:hover a{
      text-decoration: none;
      color: #50B9FF;
    }
    .tabs-component-tab:hover::after {
      background: #50B9FF;
    }
  }
  .tabs-component-tab.is-active a {
    color: rgb(0, 117, 188);
    font-weight: 600;
  }
  .tabs-component-tab.is-active::after {
    background: rgb(0, 117, 188);
  }

  /* Sidebar tab pane */
  .sidebar-content {
    position: relative;
    overflow: auto;
    padding: 1.5rem!important;
    padding-right: 0;
  }

  .sidebar-content {
    list-style: none;
    padding-left: 0;
    margin: 0;
    margin-bottom: 1rem;
    overflow: auto;
  }

  .content-item .title{
    margin: 0;
    font-size: 1.4rem;
    font-weight: inherit;
    color: rgb(0, 117, 188);
  }

  .content-item {
    margin-top: 2rem;
  }

  .sidebar-content li:first-of-type .content-item{
    margin-top: 0;
  }

  /* Sidebar close */
  #close-sidebar {
    position: absolute;
    z-index: 1;
    top: .5rem;
    right: .5rem;
    font-size: 2rem;
    color: #898989;

    .icon {
      font-size: 1rem;
      margin-right: 5px;
    }
  }

  &:not(.embedded) {
    .sidebar-content {
      max-height: ~"calc(100vh - 30rem)";
    }

    @media (max-width: 768px) {
      position: fixed;
      bottom: 1rem;
      right: 1rem;
      z-index: 200;

      width: 220px;
      /*min-width: 200px;*/
      transition: width .3s, height .3s;
      overflow: hidden;
      height: 10rem;

      &.is-expanded-on-mobile {
        height: ~"calc(100% - 8rem)";
        width: ~"calc(100% - 2rem)";
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

      .sidebar-conent {
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
      top: 40px;
      overflow-x: hidden;
      width: 320px;

      .tabs-component-tab .counter {
        display: none;
      }

      #close-sidebar {
        display: none;
      }
    }
    @media(min-width: 769px) and (max-width: 1000px) {
      width: auto;
    }

  }
}

// this style is to be applied on body. meh.
.sidebar-open {
  overflow: hidden;
  position: relative;
  height: 100%;
  position: fixed;
}

</style>


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
    }
  },

  created() {
    if (this.embedded) return

    // Add a media query listener handle mobile events
    var mq = window.matchMedia ('(max-width: 768px)');
    var self = this;
    mq.addListener(function(mq) { self.onMobile = mq.matches; });
    this.onMobile = mq.matches; // initial check;
  },

  methods: {
    mobileExpand() {
      if(this.embedded) return

      if (!this.isMobileExpanded) {
        this.isMobileExpanded = true;
        this.$el.classList.add('is-expanded-on-mobile');
        document.querySelector('body').classList.add('sidebar-open');
        document.querySelector('html').classList.add('sidebar-open');
      }
    },

    mobileCollapse(e) {
      if(this.embedded) return

      e = e || window.event;
      if(e)
      e.stopPropagation(); // event will trigger expand and cancel collapse
      if (this.isMobileExpanded) {
        this.isMobileExpanded = false;
        var el = this.$el;
        el.classList.remove('is-expanded-on-mobile');
        document.querySelector('body').classList.remove('sidebar-open')
        document.querySelector('html').classList.remove('sidebar-open')
      }
    },
  },

  watch: {
    onMobile (matches) {
      if (this.embedded) return

      if (matches) {
        this.$el.addEventListener('click', this.mobileExpand, false);
      } else {
        this.$el.removeEventListener('click', this.mobileExpand, false);
        this.mobileCollapse();
      }
    },
  },
}
</script>
