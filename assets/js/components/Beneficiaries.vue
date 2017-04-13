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
      // TODO: make this a mixin
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
        d3.csv($this.datasource, function(d, i, columns) {
          let total = 0,
              column;
          for (let j=2; j<columns.length; ++j) {
            column = columns[j];
            // (also make sure they're all ints)
            total += d[column] = +d[column];
          }
          d.total = total;
          return d;
        }, function(error, data) {
	  if (error) throw error;

          $this.drawChart(data);
        });
      }
    },

    drawChart(data) {
      const $this = this;

      data.sort((a, b) => b.total - a.total);

      // reserved for country labels
      const reserved = 120;

      const stack = d3.stack();

      const x = d3.scaleLinear()
            .range([0, this.width - reserved]);

      const y = d3.scaleBand()
            .paddingInner(0.5)
            .align(1);

      x.domain([0, d3.max(data, (d) => d.total)]);
      var keys = data.columns.slice(2);
      stack.keys(keys);

      const height = 20;
      $this.height = height * data.length;

      y.rangeRound([0, $this.height]);
      y.domain(data.map( (d) => d.name ))

      // d3.stack returns items grouped by columns (keys),
      // but we want them grouped by row
      const _stacked = stack(data);
      const xdata = d3.transpose(_stacked);

      // but this loses items' keys, so fix it
      _stacked.forEach((d) => {
        for (let item of xdata) {
          item[d.index].key = d.key;
          // and while at it, set data at row level too
          if (!item.data) item.data = item[d.index].data;
        }
      });

      const beneficiary = $this.svg.select("g.chart")
	    .selectAll(".beneficiary")
            .data(xdata)
            .enter().append("g")
              .attr("class", "beneficiary")
              .attr("transform", (d, i) => {
                return `translate(0,${y(d.data.name)})`;
              })

      // beneficiary
      //   .transition()
      //   .duration(1000)
      //   .attrTween("transform" , (d, i) => {
      //     const interpolate = d3.interpolate($this.height / 2,i * (height + spacing));
      //     return (y) => `translate(0, ${interpolate(y)})`;
      //   });

      beneficiary
        .append("title")
        .text((d) => d.data.name);

      beneficiary
        .selectAll("rect")
      // this is needed to re-iterate on inner data
        .data((d) => d)
        .enter().append("rect")
          .attr("fill", (d) => $this.colour(d.key))
          .attr("x", (d) => x(d[0]))
          .attr("y", 0)
          .attr("width", (d) => x(d[1]) - x(d[0]))
          .attr("height", y.bandwidth)
          .attr("transform", `translate(${reserved},0)`)

      // we might want to add the titles manually
      // if giving up the y() scale
      // beneficiary
      //   .append("text")
      //   .text((d) => d.data.name)

      $this.svg.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(${reserved},0)`)
        .call(d3.axisLeft(y))
    },
  },
  watch: {
    datasource: {
      handler: 'main',
    },
  },
});

</script>
