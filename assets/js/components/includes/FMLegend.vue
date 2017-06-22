<!--
    // to be used only as a sub-component of the WithFMs mixin
  -->

<template>
<ul class="fms">
  <li
      v-for="fm in fms"
      class="fm"
      :class="[
        fm.id,
        $parent.getFilterClassFm(fm),
        { zero: fm.value == 0 },
      ]"
      @click="$parent.toggleFm(fm, $event.target)"
  >
    <slot name="fm-content" :fm="fm">{{ fm.name }}</slot>
  </li>
</ul>
</template>


<style lang="less">
.legend {
  .fm {
    cursor: pointer;
    &.zero {
      cursor: not-allowed;
    }

    &.disabled, &.zero {
      filter: grayscale(100%);
      opacity: 0.5;
    }

    &.selected {
      text-shadow: 0 0 1px #999;
    }

    transition: all .5s ease;
  }
}
</style>


<script>
import Vue from 'vue';
export default Vue.extend({
     props: ['fms'],
});
</script>
