<template>
<svg class="bar-thing" :width="width" :height="height">
  <g class="chart"></g>
</svg>
</template>

<style>
.chart {}
</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';

import {FMColours} from '../constants.js';

export default Vue.extend({
  props: {
    datasource: String,
    data: Object,
    width: Number,
    height: Number,
  },

  data() {
    return {
      colour: d3.scaleOrdinal()
                .domain(d3.keys(FMColours))
                .range(d3.values(FMColours)),
    };
  },

  mounted() {
    this.svg = d3.select(this.$el);
    this.main();
  },

  methods: {
    main() {
      const $this = this;

      if ($this.data) {
        $this.drawChart($this.data);
      } else {
        d3.json($this.datasource, function(error, data) {
	  if (error) throw error;

          $this.drawChart(data);
        });
      }
    },

    drawChart(data) {
      const $this = this;

      var x = d3.scaleLinear()
          .rangeRound([0, this.width])
          .domain([0, d3.sum(d3.values(data))]);

      const bar = $this.svg.select("g.chart")
	    .selectAll(".bar")
            .data(d3.entries(data))
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
  watch: {
    datasource: {
      handler: 'main',
    },
  },
});

</script>
