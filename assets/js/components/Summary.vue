<template>
  <div v-show="hasData" :class="classNames">
    <transition name="fade">
      <div v-if="data.allocation > 0" :key="changed" class="allocation">
        <strong>{{ currency(data.allocation) }}</strong>
        <span>&nbsp;</span>
        <strong v-if="allocationType">{{ allocationType }} allocation </strong>
        <small v-if="data.bilateral_allocation">
          {{ currency(data.bilateral_allocation) }} for bilateral fund
        </small>
      </div>
      <div v-else-if="!data.allocation" class="allocation">
        <strong>No allocation available</strong>
      </div>
    </transition>
  </div>
</template>

<script>
import Component from "./Component";

export default {
  extends: Component,
  type: "summary",
  props: {
    allocationType: {
      type: String,
      required: false,
      default: "",
    },
  },
  data() {
    return {
      transitioned: false,
    };
  },

  computed: {
    data() {
      if (!this.hasData) return {};
      return this.aggregate(
        this.filtered,
        [],
        ["allocation", "bilateral_allocation"],
        false
      );
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.summary {
  position: relative;

  padding: 1rem;
  text-align: center;
  height: 60px;

  strong {
    color: #3b5998;
    font-size: larger;
  }

  small {
    display: block;
    color: #abb447;
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
