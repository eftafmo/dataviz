<!--
    // to be used only as a sub-component of the WithFMs mixin
  -->

<template>
  <ul class="fms">
    <li
      v-for="fm in fms"
      class="fm"
      :class="[fm.id, getFilterClassFm(fm), { zero: fm.allocation == 0 }]"
      @click="toggleFm(fm, $event.target)"
      :key="fm.id"
    >
      <slot name="fm-content" :fm="fm">
        <span class="fill" :style="{ backgroundColor: fm.colour }"></span>
        {{ fm.name }}
      </slot>
    </li>
  </ul>
</template>

<style lang="less">
.legend {
  .fm {
    list-style-type: none;
    @media (min-width: 800px) {
      margin-right: 2rem;
    }

    span.fill {
      display: inline-block;
      width: 10px;
      height: 10px;
    }

    cursor: pointer;
    &.zero {
      cursor: not-allowed;
      pointer-events: none;
    }

    &.disabled,
    &.zero {
      filter: grayscale(100%);
      opacity: 0.3;
    }

    transition: all 0.5s ease;
  }
}
</style>

<script>
import Vue from "vue";
export default Vue.extend({
  props: ["fms"],

  methods: {
    _findAncestorProperty(name) {
      let current = this,
        property = undefined;

      while (property === undefined) {
        current = current.$parent;
        property = current[name];
      }

      return property;
    },

    getFilterClassFm(fm) {
      const func = this._findAncestorProperty("getFilterClassFm");
      return func(fm);
    },

    toggleFm(fm, etarget) {
      const func = this._findAncestorProperty("toggleFm");
      return func(fm, etarget);
    },
  },
});
</script>
