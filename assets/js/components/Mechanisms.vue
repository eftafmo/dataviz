<template>
<div :class="classNames">
  <slot name="title" v-if="!this.embedded"></slot>
  <dropdown v-if="rendered" filter="fm" title="No filter selected" :items="nonzero"></dropdown>
  <svg viewBox="0 0 100 10"  preserveAspectRatio="none">
    <g class="chart"></g>
  </svg>
  <div v-if="hasData" class="legend">
    <slot name="legend" :data="data">
      <fm-legend :fms="data" class="clearfix">
        <template slot="fm-content" slot-scope="x">
          <span class="value" :style="{color: x.fm.colour}">{{ currency(x.fm.allocation || 0) }}</span>
          <span class="name">{{ x.fm.name }}</span>
        </template>
      </fm-legend>
    </slot>
  </div>
</div>
</template>


<style lang="less">
.dataviz .viz.fms {
  position: relative;

  svg {
    width: 100%;
    height: 3rem;

    @media (min-width:600px)and(max-width:1400px){
      width: 90%;
      margin-left: auto;
      margin-right: auto;
    }
  }

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
    .fm {
      display: inline-block;
      border-right: 1px solid #ccc;
      padding: 0 2rem;

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
.dataviz-tooltip.fms {
    line-height: 1.2;
    white-space: normal;
    &:after {
    top: 19px;
    transform: rotate(180deg);
    }
  }

</style>


<script>
import * as d3 from 'd3';
import d3tip from 'd3-tip';
import {colour2gray, slugify} from '@js/lib/util';

import Chart from './Chart';

import WithFMsMixin from './mixins/WithFMs';
import WithTooltipMixin from './mixins/WithTooltip';


export default {
  extends: Chart,
  type: "fms",

  mixins: [
    WithFMsMixin,
    WithTooltipMixin,
  ],

  props: {
    disabled_colour: {
      type: String,
      default: "#ccc",
    },
  },

  created() {
    // don't filter by fm
    const idx = this.filter_by.indexOf("fm");

    if (idx !== -1)
      this.filter_by.splice(idx, 1);
  },

  data() {
    return {
      aggregate_by: [
        {source: 'fm', destination: 'name'}
      ],

      inactive_opacity: .7,
    };
  },

  computed: {
    data() {
      const aggregated = this.aggregated;

      // base the data on the FM list from constants,
      // so even non-existing FMs get a 0 entry
      const out = [];
      for (const fm in this.FMS) {
        const basefm = this.FMS[fm];
        let item = aggregated[basefm.name];

        if (item === undefined) {
          // mirror an existing object
          item = {};
          const sample = d3.values(aggregated)[0];
          for (var k in sample) {
            item[k] = sample[k].constructor();
          }
        }

        Object.assign(item, basefm);
        out.push(item);
      }

      return out;
    },

    nonzero() {
      return this.data.filter( (d) => d.allocation != 0 );
    },
  },

  methods: {
    tooltipTemplate(d) {
      return `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <div class="subtitle-container">
          <span class="donor-states">${d.donor_list}</span>
        </div>
        <ul>
          <li>${this.currency(d.allocation)}</li>
          <li>${d.beneficiaries.size()} `+  this.singularize(`beneficiary states`, d.beneficiaries.size()) + `</li>
          <li>${d.sectors.size()} `+  this.singularize(`sectors`, d.sectors.size()) + `</li>
          <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
          <li>${d.programmes.size()}  `+  this.singularize(`programmes`, d.programmes.size()) + `</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
      `;
    },

    createTooltip() {
      const $this = this;

      let tip = d3tip()
          .attr('class', 'dataviz-tooltip fms')
          .html(this.tooltipTemplate)
          .direction('s')
          .offset([0, 0])

       this.tip = tip;
       this.chart.call(this.tip)
    },

    renderChart() {
      const $this = this,
            chart = this.chart;

      const t = this.getTransition();

      // we always use width 100, because viewBox and preserveAspectRatio=none
      const width = 100;

      const x = d3.scaleLinear()
          .rangeRound([0, width])
          .domain([0, d3.sum(this.data.map( (d) => d.allocation ))]);

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
        //.attr("width", (d) => x(d.allocation) )
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
        .attr("width", (d) => x(d.allocation) );

      fms.select("rect")
        .transition(t)
        .attr("width", (d) => x(d.allocation) );
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
}
</script>
