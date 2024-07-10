<!--
    // to be used only as a sub-component of the WithFMs mixin
  -->

<template>
  <ul class="fms">
    <li
      v-for="fm in fms"
      :key="fm.id"
      class="fm"
      :class="[fm.id, getFilterClassFm(fm), { zero: fm.allocation === 0 }]"
      @click="toggleFm(fm, $event.target)"
    >
      <slot name="fm-content" :fm="fm">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
          <rect width="10" height="10" :fill="fm.stripesFill"></rect>
        </svg>
        {{ fm.name }}
      </slot>
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    fms: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
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
};
</script>

<style lang="less">
.legend {
  .fm {
    list-style-type: none;
    @media (min-width: 800px) {
      margin-right: 2rem;
    }

    .fill {
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
