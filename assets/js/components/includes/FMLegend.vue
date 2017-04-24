<!--
    // to be used only as a sub-component of the WithFMs mixin
  -->

<template>
<div class="fms">
<ul>
  <li
      v-for="(fm, k, index) in fms"
      class="fm"
      :class="[fm.id, $parent.getFilterClass(fm)]"
      @click="$parent.toggleFm(fm, $event.target)"
  >
    <slot name="fm-content" :fm="fm">{{ fm.name }}</slot>
  </li>
</ul>
<select @change="$parent.triggerclick()">
 <option value="" class="" @click="$parent.resetfilter()">Select financial mechanism</option>
  <option
      v-for="(fm, k, index) in fms"
      class="fm"
      :class="[fm.id, $parent.getFilterClass(fm)]"
      @click="$parent.toggleFm(fm, $event.target)"
      :value="fm.name"
  >
    <slot name="fm-content" :fm="fm">{{ fm.name }}</slot>
  </option>
</select>
</div>
</template>

<style lang="less">
  select {
    position: absolute;
    top: 30px;
    right: 0;
    border-color: #fff;
    background: #fff;
    color: #aaa;
    &:focus {
      outline: none;
    }
    option {
      color: black;
    }
  }
</style>

<script>
import Vue from 'vue';
export default Vue.extend({
     props: ['fms'],
});
</script>
