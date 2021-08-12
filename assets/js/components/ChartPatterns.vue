<template>
  <defs>
    <pattern
      v-for="fmData in FM_ARRAY"
      :id="`stripes-pattern-${fmData.id}`"
      :key="fmData.id"
      width="6"
      height="20"
      patternTransform="rotate(45 0 0)"
      patternUnits="userSpaceOnUse"
    >
      <rect width="6" height="20" :fill="fmData.colour"></rect>
      <line
        x1="0"
        y1="0"
        x2="0"
        y2="20"
        stroke-width="1"
        vector-effect="non-scaling-stroke"
        :stroke="fmData.pattern"
      />
    </pattern>
  </defs>
</template>

<script>
import WithFMs from "./mixins/WithFMs";

export default {
  name: "ChartPatterns",
  mixins: [WithFMs],
};
</script>

<style scoped></style>