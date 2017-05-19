<template>
<div class="fms-viz">
  <chart-container :width="width">
    <svg viewBox="0 0 100 10"  preserveAspectRatio="none">
      <g class="chart"></g>
    </svg>
  </chart-container>
  <div v-if="hasData" class="legend">
    <fm-legend :fms="fms" class="clearfix">
      <template slot="fm-content" scope="x">
        <span class="value" :style="{color: colour(x.fm)}">{{ format(value(x.fm)) }}</span>
        <span class="name">{{ x.fm.name }}</span>
      </template>
    </fm-legend>
  </div>
  <div v-if="hasData" class="dropdown">
    <dropdown filter="fm" title="Both financial mechanisms" :items="fms"></dropdown>
  </div>
</div>
</template>


<style lang="less">
.fms-viz {
  svg {
    width: 100%;
    height: 3rem;
  }
  .chart-container {
    width: 100%;
    height: 3rem;

   & > svg, & > canvas {
      height: 100%;
    }

    @media (min-width:600px)and(max-width:1400px){
      width: 90%;
      margin-left: auto;
      margin-right: auto;
    }

  }

  text-align: center;
  .fms {
    text-align: center;
  }

  .fm { cursor: pointer; }

  .legend .fm {
    transition: all .5s ease;
  }
  .legend .fm.disabled {
    filter: grayscale(100%);
    opacity: 0.5;
  }

  .legend .fm.selected {
    text-shadow: 0 0 1px #999;
  }

  .legend .fm {
    list-style-type: none;
    display: inline-block;
  }

  .legend .fm {
    border-right: 1px solid #ccc;
    padding: 0 2rem;
  }

  .legend .fm:last-of-type {
    padding-right: 0;
    border-right: none;
  }

  .legend .fm:first-of-type {
    padding-left: 0;
  }

  .legend .value {
    font-size: 1.8rem;
    font-weight: bold;
  }

  .legend .fm .name {
    display: block;
  }
}

</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';
import {colour2gray} from 'js/lib/util';

import BaseMixin from './mixins/Base.vue';
import ChartMixin from './mixins/Chart.vue';
import WithFMsMixin from './mixins/WithFMs.vue';

import FMs from 'js/constants/financial-mechanisms.json5';


export default Vue.extend({
  mixins: [BaseMixin, ChartMixin, WithFMsMixin],

  props: {
    disabled_colour: {
      type: String,
      default: "#ccc",
    },
  },

  data() {
    return {
      inactive_opacity: .7,
      width: 100,
    };
  },

  methods: {
    value(fm) {
      const fmid = this.getFmId(fm);
      return this.data[fmid] || 0;
    },

    renderChart() {
      const $this = this,
            chart = this.chart;

      // we always use width 100, because viewBox and preserveAspectRatio=none

      const x = d3.scaleLinear()
          .rangeRound([0, this.width])
          .domain([0, d3.sum(d3.values(this.data))]);

      const fms = chart
	    .selectAll(".fm")
            .data(d3.entries(this.data))
            .enter().append("rect")
            .attr("class", (d) => "fm " + d.key);

      fms
        .attr("x", 0)
        .attr("y", 0)
      // skip this here to transition it below
      //.attr("width", (d) => x(d.value))
        .attr("height", "100%")
        .attr("transform", (d, i) => {
          // draw the second bar from right to left
          if (i == 1) return (
            `scale(-1,1) translate(-${this.width},0)`
          );
        })
        .attr("fill", (d) => this.colour(d))
        .transition()
        .duration(500)
        .attr("width", (d) => x(this.value(d)));

      fms
        .append("title").text((d) => this.format(this.value(d)));
      fms
        .append("desc").text((d) => this.fms[d.key].name);

      fms
        .on("click", function (d) {
          $this.toggleFm(d, this);
        });

      // remember the current selection, we'll use it for transitions
      this._chart_fms = fms;
    },

    handleFilterFm(val, old) {
      // transition the chart to disabled / selected.
      // (the legend is handled by vue.)

      // TODO: handle the case when !this.isReady()
      this._chart_fms
        .transition()
        .duration(500)
        .attr("fill", (d) => (
          this.isDisabled(d) ?
            colour2gray(this.colour(d), this.inactive_opacity) :
            this.colour(d)
        ));
    },
  },
});

</script>
