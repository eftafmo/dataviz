<template>
  <div :class="classNames" v-show="hasData">
    <transition name="fade">
      <div class="allocation" :key="changed" v-if="data.allocation > 0">
        <strong>{{ currency(data.allocation) }}</strong>
        <small
          >{{ currency(data.bilateral_allocation) }} for bilateral fund</small
        >
      </div>
      <div class="allocation" :key="changed" v-if="!data.allocation">
        <strong>No allocation available</strong>
      </div>
    </transition>
  </div>
</template>

<style lang="less">
.dataviz .viz.summary {
  position: relative;

  padding: 1rem;
  text-align: center;
  height: 60px;

  strong {
    color: rgb(0, 117, 188);
    font-size: larger;
  }

  small {
    display: block;
    color: #2fb82a;
  }

  .allocation {
    width: 100%;

    &.fade-enter-active {
      position: absolute;
      top: 1rem;
      width: calc(~"100% - 2rem");
    }

    &.fade-leave-active {
      position: absolute;
      top: 1rem;
      width: calc(~"100% - 2rem");
    }
  }

  &:not(.embedded) {
    @media (max-width: 768px) {
      padding-bottom: 0;

      small {
        font-size: 1rem;
      }
    }
  }
}

.sidebar-tab-content .active {
  display: block;
}
</style>

<script>
import Component from "./Component";

export default Component.extend({
  type: "summary",

  data() {
    return {
      transitioned: false,
    };
  },

  computed: {
    data() {
      if (!this.hasData) return {};

      const out = this.aggregate(
        this.filtered,
        [],
        ["allocation", "bilateral_allocation"],
        false
      );

      return out;
    },
  },
});
</script>
