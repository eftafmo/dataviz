<template>
<div class="beneficiaries-viz">
  <div v-if="hasData" class="legend">
    <fm-legend :fms="fms" class="clearfix">
      <template slot="fm-content" scope="x">
        <span :style="{backgroundColor: x.fm.colour}"></span>
        {{ x.fm.name }}
      </template>
    </fm-legend>
  </div>
  <svg :width="width" :height="height">
    <g class="chart"></g>
  </svg>
</div>

</template>


<style lang="less">
.beneficiaries-viz {
  .legend .fm span {
    width: 10px; height: 10px;
    display: inline-block;
  }
  .legend li {
    list-style-type: none;
    display: inline-block;
    margin-right: 2rem;
  }
}

</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import CSVReadingMixin from './mixins/CSVReading';
import WithFMsMixin from './mixins/WithFMs';

// load all country flags as sprites
import _countries from 'js/constants/countries.json5';

function _get_flag_name(c) {
  const flag = c.toLowerCase().replace(/ /g, '');
  return `flag-${flag}`;
}

const _req = require.context('svg-sprite-loader!imgs', false, /flag-[a-z]+\.png$/);
// we could load all of _req.keys(), but we want things to fail
// if there's a mismatch between country names and png files
// (possible TODO: compare _req.keys() with _countries and warn if necessary )
for (let _c of _countries) {
  const req = require.context('svg-sprite-loader!imgs', false, /flag-[a-z]+\.png$/);
  req(`./${_get_flag_name(_c)}.png`);
}


export default Vue.extend({
  mixins: [
    BaseMixin, CSVReadingMixin,
    ChartMixin, WithFMsMixin,
  ],

  props: {
    width: Number,
    minHeight: {
      type: Number,
      default: 0,
    },
    itemHeight: {
      type: Number,
      default: 20,
    },
    reserved: {
      // reserved for country labels. TODO: change this name
      type: Number,
      default: 120,
    },
  },

  data() {
    return {
      height: this.minHeight,
    };
  },

  computed: {
    x() {
      return d3.scaleLinear()
               .range([0, this.width - this.reserved])
               .domain([0, d3.max(this.data, (d) => d.total)]);
    },

    y() {
      return d3.scaleBand()
               .paddingInner(0.5) // TODO: propify
               .align(1)  // TODO: propify
               .rangeRound([0, this.height])
               .domain(this.data.map( (d) => d.name ));
    },
  },

  methods: {
    processRow(d, i, columns) {
      let total = 0,
          column;
      // compute a total for each row
      for (let j=2; j<columns.length; ++j) {
        column = columns[j];
        // (also make sure they're all ints)
        total += d[column] = +d[column];
      }
      d.total = total;

      return d;
    },

    processData(data) {
      // sort it from the start.
      // (sorting it later would cause data to mutate, which is bad)
      return data.sort((a, b) => b.total - a.total);
    },

    yAxis(g) {
      // customizes the axis to add country flags
      const axis = d3.axisLeft(this.y)
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
    },

    renderChart() {
      const $this = this;

      // resize the chart to fit the data
      this.height = Math.max(this.minHeight,
                              this.itemHeight * this.data.length);

      const stack = d3.stack()
                      .keys(this.data.columns.slice(2))

      // transpose because we want items grouped by row.
      // (d3.stack returns items grouped by columns (keys))
      const _stacked = stack(this.data),
            data = d3.transpose(_stacked);

      // but this loses items' keys, so fix it
      _stacked.forEach((d) => {
        for (let item of data) {
          item[d.index].key = d.key;
          // and while at it, set data at row level too
          if (!item.data) item.data = item[d.index].data;
        }
      });

      const chart = $this.chart;

      const beneficiary = chart
	    .selectAll(".beneficiary")
            .data(data)
            .enter().append("g")
              .attr("class", "beneficiary")
              .attr("transform", (d, i) => {
                const y = $this.y(d.data.name);
                return `translate(0,${y})`;
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
          .attr("x", (d) => $this.x(d[0]))
          .attr("y", 0)
          .attr("width", (d) => $this.x(d[1]) - $this.x(d[0]))
          .attr("height", $this.y.bandwidth)
          .attr("transform", `translate(${$this.reserved},0)`)

      // we might want to add the titles manually
      // if giving up the y() scale
      // beneficiary
      //   .append("text")
      //   .text((d) => d.data.name)

      chart.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(${$this.reserved},0)`)
        .call($this.yAxis)
    },
  },
  watch: {
    datasource: {
      handler: 'main',
    },
  },
});

</script>
