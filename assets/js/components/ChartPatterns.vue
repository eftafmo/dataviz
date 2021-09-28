<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    class="patterns-def"
    width="6"
    height="20"
  >
    <defs>
      <pattern
        v-for="item in patterns"
        :id="`stripes-pattern-${item.id}`"
        :key="item.id"
        width="6"
        height="20"
        patternTransform="rotate(45 0 0)"
        patternUnits="userSpaceOnUse"
      >
        <rect width="100%" height="100%" :fill="item.color"></rect>
        <line
          x1="0"
          y1="0"
          x2="0"
          y2="100%"
          stroke-width="1"
          :stroke="item.pattern"
        />
      </pattern>
    </defs>
  </svg>
</template>

<script>
import WithFMs from "./mixins/WithFMs";

export default {
  name: "ChartPatterns",
  props: {
    patterns: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped lang="less">
.patterns-def {
  position: absolute;
  pointer-events: none;
}
</style>