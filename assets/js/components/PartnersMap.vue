<template>
<div :class="[$options.type, { rendering: !rendered }]">
  <h2>{{title}}</h2>
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
      title: 'Network map'
    };
  },

  methods: {
    renderChart() {
      //
    },
  },
});
</script>
