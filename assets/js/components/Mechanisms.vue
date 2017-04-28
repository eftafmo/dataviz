<template>
<div class="fms-viz">
  <svg :width="width" :height="height">
    <g class="chart"></g>
  </svg>
  <div v-if="hasData" class="legend">
    <fm-legend :fms="fms" class="clearfix">
      <template slot="fm-content" scope="x">
        <span class="value" :style="{color: colour(x.fm)}">{{ format(value(x.fm)) }}</span>
        <span class="name">{{ x.fm.name }}</span>
      </template>
    </fm-legend>
  </div>
  <div v-if="hasData" class="dropdown">
    <dropdown filter="fm" title="Select a financial mechanism" :items="fms"></dropdown>
  </div>
</div>
</template>


<style lang="less">
.fms-viz {
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
    border-right: 1px solid #aaa;
    padding-right:2rem;
  }

  .legend .fm:last-of-type {
    padding-left: 2rem;
    border-right: none;
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

import BaseMixin from './mixins/Base.vue';
import ChartMixin from './mixins/Chart.vue';
import WithFMsMixin from './mixins/WithFMs.vue';
import Dropdown from './includes/DropdownFilter.vue';

import FMs from 'js/constants/financial-mechanisms.json5';


export default Vue.extend({
  mixins: [BaseMixin, ChartMixin, WithFMsMixin],

  components: {
    'dropdown': Dropdown,
  },

  props: {
    width: Number,
    // refers to the chart height only
    height: {
      type: Number,
      default: 40,
    },
    disabled_colour: {
      type: String,
      default: "#ccc",
    },
  },

  methods: {
    value(fm) {
      const fmid = this.getFmId(fm);
      return this.data[fmid] || 0;
    },

    renderChart() {
      const $this = this,
            _root = d3.select(this.$el),
            chart = _root.select("svg").select("g.chart");

      var x = d3.scaleLinear()
          .rangeRound([0, this.width])
          .domain([0, d3.sum(d3.values(this.data))]);

      const fms = chart
	    .selectAll(".fm")
            .data(d3.entries(this.data))
            .enter().append("rect")
            .attr("class", (d) => "fm " + d.key);

      fms
        .attr("x", (d) => 0)
        .attr("y", (d) => 0)
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

      // remember the current selection, we'll use it for transitionsc
      this._chart_fms = fms;
    },

    handleFilterFm(val, old) {
      // transition the chart to disabled / selected.
      // (the legend is handled by vue.)

      // TODO: handle the case when !this.isReady()
      this._chart_fms
        .transition()
        .duration(500)
        .attr("fill", (d) => (this.isDisabled(d) ?
                              this.disabled_colour : this.colour(d))
        );
    },
  },
});

</script>