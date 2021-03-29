<!--
     use this for SVGs with viewBox to get them to properly scale on IE:

     <chart-container :width="width" :height="height">
       <svg :viewBox="`0 0 ${width} ${height}`">
         ...
       </svg>
     </chart-container>

-->

<template>
  <div class="chart-container">
    <!-- "the canvas trick": http://stackoverflow.com/a/30416241 -->
    <canvas :width="width" :height="height" />
    <slot />
  </div>
</template>

<style lang="less">
.dataviz .viz .chart-container {
  position: relative;
  width: 100%;

  & > svg,
  & > canvas {
    display: block;
    width: 100%;
  }
  & > canvas {
    visibility: hidden;
  }
  & > svg {
    position: absolute;
    top: 0;
    left: 0;
  }
}
</style>

<script>
export default {
  props: {
    width: Number,
    height: Number,
  },
};
</script>
