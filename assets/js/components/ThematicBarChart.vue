<template>
  <bar-chart
    main-filter="thematic"
    embed-tag="thematic_bar_chart"
    title="Working together for..."
    drop-down-title="Criteria"
    :all-items="themeArray"
    allocation-field="net_allocation"
    allocation-type="net"
  />
</template>

<script>
import themeArray from "@js/constants/thematic.json5";
import BarChart from "./BarChart";

export default {
  name: "ThematicBarChart",
  components: { BarChart },
  data() {
    return {
      themeArray,
    };
  },
};
</script>

<style lang="less">
</style>