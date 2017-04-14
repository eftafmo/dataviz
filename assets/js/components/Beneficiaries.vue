<template>
<svg class="bar-thing" :width="width" :height="height">
  <!-- TODO: move this to html? -->
  <g class="fms">
    <g v-for="(fm, k, index) in fms"
       @click="filterFM(fm, $event)"
       :class="'fm ' + fm.id"
       :transform="`translate(${+index * 150},0)`"> {{ index }}
      <!-- add a transparent rect to give it some clicking room -->
      <rect width="26" height="16" transform="translate(-3,-3)" fill="transparent" />
      <rect width="10" height="10" :fill="fm.colour" />
      <text x="20" dy=".71em">{{ fm.name }}</text>
    </g>
  </g>
  <g class="chart" transform="translate(0, 30)">
  </g>
</svg>
</template>

<style>
.fms .fm { cursor: pointer; }
.chart {}
</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';

import {FMColours} from '../constants.js';
import FMs from 'js/constants/financial-mechanisms.json5';

// load all country flags as sprites
import _countries from 'js/constants/countries.json5';

function _get_flag_name(c) {
  const flag = c.toLowerCase().replace(/ /g, '');
  return `flag-${flag}`;
}

const _req = require.context('svg-sprite-loader!imgs', false, /flag-[a-z]+\.png$/);
// we could load all of _req.keys(), but we want things to fail
// if there's a mismatch between country names and png files
for (let _c of _countries) {
  const req = require.context('svg-sprite-loader!imgs', false, /flag-[a-z]+\.png$/);
  req(`./${_get_flag_name(_c)}.png`);
}
// TODO: compare _req.keys() with _countries and warn if necessary


export default Vue.extend({
  props: {
    datasource: String,
    data: Object,
    width: Number,
    minHeight: {
      type: Number,
      default: 0,
    },
  },

  data() {
    return {
      fms: FMs,
      // TODO: make this a mixin
      colour: d3.scaleOrdinal()
                .domain(d3.keys(FMColours))
                .range(d3.values(FMColours)),
      height: this.minHeight,
    };
  },

  mounted() {
    this.svg = d3.select(this.$el);
    this.main();
  },

  methods: {
    filterFM(fm, e)  {
      console.log(fm);
      console.log(e);
    },
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

      // customize the axis to add country flags
      function customYAxis(g) {
        const axis = d3.axisLeft(y)
              .tickSize(0)

        g.call(axis);

        const ticks = g.selectAll('.axis .tick');
        // colorize domain bar
        g.select('.axis .domain').attr('stroke', '#ccc');
        // remove invisible ticks
        ticks.select('line').remove();
        // move text
        ticks.select('text').attr('x', -30);
        ticks
          .append('use')
          .attr('xlink:href', (d) => `#${_get_flag_name(d)}`)
          .attr('viewBox', '0 0 30 20')
          .attr('transform', 'translate(-23,-6) scale(0.035,0.035)');

        /*
        s.select(".domain").remove();
        s.selectAll(".tick line").filter(Number).attr("stroke", "#777").attr("stroke-dasharray", "2,2");
        s.selectAll(".tick text").attr("x", 4).attr("dy", -4);
        if (s !== g) g.selectAll(".tick text").attrTween("x", null).attrTween("dy", null);
        */
      }

      x.domain([0, d3.max(data, (d) => d.total)]);
      var keys = data.columns.slice(2);
      stack.keys(keys);

      const height = 20;
      $this.height = Math.max(this.minHeight, height * data.length);

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


      const chart = $this.svg.select("g.chart")

      const beneficiary = chart
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

      chart.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(${reserved},0)`)
        .call(customYAxis)
    },
  },
  watch: {
    datasource: {
      handler: 'main',
    },
  },
});

</script>
