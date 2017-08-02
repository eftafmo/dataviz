<template>
<div class="map-viz partnerships" :class="{ rendering: !rendered }">

  <map-base
      ref="base"
      v-on:rendered="baseRendered"
      :origin="origin"
  >
  </map-base>

</div>
</template>


<style lang="less">
.map-viz.partnerships {

}
</style>


<script>
import * as d3 from 'd3';

import Chart from './Chart';

import MapMixin from './mixins/Map';


export default Chart.extend({
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
