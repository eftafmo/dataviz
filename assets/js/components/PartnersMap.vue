<template>
<div :class="[$options.type, { rendering: !rendered }]">

  <map-base
      ref="base"
      v-on:rendered="baseRendered"
      :origin="origin"
  >
  </map-base>

</div>
</template>


<style lang="less">
.viz.map.partnerships {

}
</style>


<script>
import * as d3 from 'd3';

import Chart from './Chart';

import MapMixin from './mixins/Map';


export default Chart.extend({
  type: "partnerships",

  mixins: [
    MapMixin,
  ],

  data() {
    return {
    };
  },

  methods: {
    renderChart() {
      //
    },
  },
});
</script>
