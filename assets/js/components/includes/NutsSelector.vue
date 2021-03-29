<template>
  <div class="nuts-selector">
    <label>NUTS level</label>
    <div>
      <input
        type="range"
        :min="min"
        :max="max"
        :step="step"
        v-model.number="level"
      />
      <label v-for="l in levels" @click="level = l">{{ l }}</label>
    </div>
  </div>
</template>

<style lang="less">
.dataviz .nuts-selector {
  padding: 7px 10px;
  background-color: rgba(249, 249, 249, 0.7);

  border: 1px solid #bbc;
  border-radius: 2px;

  opacity: 0.5;

  &.fade-enter,
  &.fade-leave-to {
    opacity: 0;
  }

  &:hover {
    opacity: 1;
    background-color: rgba(255, 255, 255, 0.9);
    border-color: #aab;
  }

  &.fade-leave-active {
    pointer-events: none;
  }

  white-space: nowrap;

  * {
    vertical-align: middle;
  }

  label {
    display: block;
    float: left;
  }

  div {
    float: right;
    margin-left: 1em;

    input {
      background: none;
      display: block;
      width: 6rem;
    }

    label {
      float: left;
      display: block;
      width: 20%;
      cursor: pointer;

      &:nth-of-type(2):not(:last-of-type) {
        text-align: center;
        margin: 0 20%;
      }
      &:last-of-type {
        text-align: right;
        float: right;
      }
    }
  }
}
</style>

<script>
export default {
  props: {
    levels: {
      type: Array,
      default: () => [1, 2, 3],
    },

    value: {
      type: Number,
      default: 3,
    },
  },

  data() {
    return {
      level: this.value,
    };
  },

  computed: {
    min() {
      return this.levels[0];
    },
    max() {
      return this.levels[this.levels.length - 1];
    },
    step() {
      return this.levels[1] - this.levels[0];
    },
  },

  watch: {
    level(v) {
      this.$emit("input", v);
    },
  },
};
</script>
