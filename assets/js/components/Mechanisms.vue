<template>
<div class="fms-viz">
  <div v-if="rendered" class="dropdown">
    <dropdown filter="fm" title="Both financial mechanisms" :items="nonzero"></dropdown>
  </div>
  <svg viewBox="0 0 100 10"  preserveAspectRatio="none">
    <g class="chart"></g>
  </svg>
  <div v-if="hasData" class="legend">
    <fm-legend :fms="data" class="clearfix">
      <template slot="fm-content" scope="x">
        <span class="value" :style="{color: x.fm.colour}">{{ currency(x.fm.value) }}</span>
        <span class="name">{{ x.fm.name }}</span>
      </template>
    </fm-legend>
  </div>
</div>
</template>


<style lang="less">
.fms-viz {

  svg {
    width: 100%;
    height: 3rem;

    @media (min-width:600px)and(max-width:1400px){
      width: 90%;
      margin-left: auto;
      margin-right: auto;
    }
  }

  text-align: center;
  .fms {
    text-align: center;
    padding-left: 0;
  }

  .chart {
    .fm {
      cursor: pointer;
      rect {
        shape-rendering: crispEdges;
      }
    }
  }

  .legend {
    .fm.disabled {
        filter: grayscale(100%);
        opacity: 0.5;
      }

     .fm.selected {
        text-shadow: 0 0 1px #999;
      }

    .fm {
      list-style-type: none;
      display: inline-block;
      border-right: 1px solid #ccc;
      padding: 0 2rem;
      transition: all .5s ease;

      @media(min-width: 400px) {
       min-width: 150px;
      }

      &:last-of-type {
        padding-right: 0;
        border-right: none;
      }

      &:first-of-type {
        padding-left: 0;
      }

      .name {
        display: block;
      }

      .value {
        font-size: 1.8rem;
        font-weight: bold;
      }
     }
    }
}
.d3-tip.fms {
    line-height: 1.2;
    white-space: normal;
    &:after {
    top: 19px;
    transform: rotate(180deg);
    }
  }

</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';
import {colour2gray, slugify} from 'js/lib/util';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithFMsMixin from './mixins/WithFMs';
import WithTooltipMixin from './mixins/WithTooltip';


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithFMsMixin,
    WithTooltipMixin,
  ],

  props: {
    disabled_colour: {
      type: String,
      default: "#ccc",
    },
  },

  data() {
    return {
      // we don't filter by fm
      filterable: ["beneficiary", "sector", "area"],

      inactive_opacity: .7,
    };
  },

  computed: {
    data() {
      const aggregated = this.aggregate(
        this.filtered,
        [{source: 'fm', destination: 'name'}],
        [
          {source: 'allocation', destination: 'value'},
          //'bilateral_allocation',
          'project_count',
          //'project_count_positive',
          //'project_count_ended',
          {source: 'beneficiary', destination: 'beneficiaries', type: String, filter_by: 'is_not_ta'},
          {source: 'sector', destination: 'sectors', type: String, filter_by: 'is_not_ta'},
          {source: 'area', destination: 'areas', type: String, filter_by: 'is_not_ta'},
          {source: 'programmes', destination: 'programmes', type: Object, filter_by: 'is_not_ta'},
        ],
        false
      );

      // base the data on the FM list from constants,
      // so even non-existing FMs get a 0 entry
      const out = [];
      for (const fm in this.FMS) {
        const basefm = this.FMS[fm];

        const item = {
          value: 0,
          project_count: 0,
          beneficiaries: d3.set(),
          sectors: d3.set(),
          areas: d3.set(),
        };

        Object.assign(item, basefm, aggregated[basefm.name]);
        out.push(item);
      }

      return out;
    },

    nonzero() {
      return this.data.filter( (d) => d.value != 0 );
    },
  },

  methods: {
    tooltipTemplate(d) {
      return `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <ul>
          <li>${this.currency(d.value)}</li>
          <li>${d.beneficiaries.size()} `+  this.singularize(`beneficiary states`, d.beneficiaries.size()) + `</li>
          <li>${d.sectors.size()} `+  this.singularize(`priority sectors`, d.sectors.size()) + `</li>
          <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
          <li>${d.programmes.size()}  `+  this.singularize(`programmes`, d.programmes.size()) + `</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
      `;
    },

    createTooltip() {
      const $this = this;

      let tip = d3.tip()
          .attr('class', 'd3-tip fms')
          .html(this.tooltipTemplate)
          .direction('s')
          .offset([0, 0])

       this.tip = tip;
       this.chart.call(this.tip)
    },

    renderChart() {
      const $this = this,
            chart = this.chart;

      // special trick to animate this on first render too
      this.rendered = true;
      const t = this.getTransition();

      // we always use width 100, because viewBox and preserveAspectRatio=none
      const width = 100;

      const x = d3.scaleLinear()
          .rangeRound([0, width])
          .domain([0, d3.sum(this.data.map( (d) => d.value ))]);

      const fms = chart.selectAll("g.fm")
                       .data(this.data, (d) => d.id );
      const fentered = fms.enter().append("g")
                          .attr("class", (d) => "fm " + d.id );
      fentered
        .call(this.renderColours)
      .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("height", "100%")
        // start with a 0-width so we transition this during enter too
        //.attr("width", (d) => x(d.value) )
        .attr("width", 0)
        .attr("transform", (d, i) => {
          // draw the second bar from right to left
          if (i == 1) return (
            `scale(-1,1) translate(-${width},0)`
          );
        })
        .on("click", function (d) {
          $this.toggleFm(d, this);
        })
        .on("mouseenter", this.tip.show)
        .on("mouseleave", this.tip.hide)

        .transition(t)
        .attr("width", (d) => x(d.value) );

      fms.select("rect")
        .transition(t)
        .attr("width", (d) => x(d.value) );
    },

    renderColours(selection) {
      selection
        .attr("fill", (d) => (
          this.isDisabledFm(d) ?
          colour2gray(d.colour, this.inactive_opacity) :
          d.colour
        ) );
    },

    handleFilterFm(val, old) {
      // transition the chart to disabled / selected.
      // (the legend is handled by vue.)
      this.chart.selectAll("g.fm")
          .transition(this.getTransition())
          .call(this.renderColours);
    },
  },
});

</script>
