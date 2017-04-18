<template>
<div class="bar-thing">
  <svg :width="width" :height="height">
    <g class="chart"></g>
  </svg>
  <div v-if="data" class="legend">
    <ul class="fms">
      <li v-for="(fm, k, index) in fms"
          @click="filterFM(fm, $event)"
          :class="'fm ' + fm.id"
      >
        <span :style="{backgroundColor: colour(fm.id)}"></span>
        {{ fm.name }}
        - {{ format(fm.value) }}
      </li>
    </ul>
  </div>
</div>
</template>


<style>
.fm { cursor: pointer; }
.legend .fm span {
  width: 10px; height: 10px;
  display: inline-block;
}
</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';

import BaseMixin from './mixins/Base.vue';
import WithFMsMixin from './mixins/WithFMs.vue';

import FMs from 'js/constants/financial-mechanisms.json5';


export default Vue.extend({
  mixins: [BaseMixin, WithFMsMixin],

  props: {
    width: Number,
    height: Number,
  },

  computed: {
    fms() {
      const fms = Object.assign({}, FMs);
      for (let fm in fms) {
        fms[fm].value = this.data[fm] || 0;
      }
      return fms;
    },
  },

  methods: {
    main() {
      this.renderChart();
    },

    renderChart() {
      const $this = this,
            _root = d3.select(this.$el),
            chart = _root.select("svg").select("g.chart");

      var x = d3.scaleLinear()
          .rangeRound([0, this.width])
          .domain([0, d3.sum(d3.values($this.data))]);

      const bar = chart
	    .selectAll(".bar")
            .data(d3.entries($this.data))
            .enter().append("rect")
            .attr("x", (d) => 0)
            .attr("y", (d) => 0)
            //.attr("width", (d) => x(d.value))
            .attr("height", 10)
            .attr("transform", (d, i) => {
              if (i == 1) return `scale(-1,1)
                                  translate(-${this.width},0)`;
            })
            .attr("fill", (d) => $this.colour(d.key))
            .transition()
            .duration(500)
            .attr("width", (d) => x(d.value));
    },
  },
});

</script>
