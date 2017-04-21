<!--
    // to be used only as a sub-component of the WithFMs mixin
  -->

<template>
<ul class="fms">
  <li
      v-for="(fm, k, index) in fms"
      class="fm"
      :class="[fm.id, $parent.getFilterClass(fm)]"
      @click="$parent.toggleFm(fm, $event.target)"
  >
    <slot name="fm-content" :fm="fm">{{ fm.name }}</slot>
  </li>
</ul>
</template>


<script>
import Vue from 'vue';

export default Vue.extend({
     props: ['fms'],
});
</script>
