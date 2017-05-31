<template>
<div class="fms-viz">
  <svg viewBox="0 0 100 10"  preserveAspectRatio="none">
    <g class="chart"></g>
  </svg>
  <div v-if="hasData" class="legend">
    <fm-legend :fms="data" class="clearfix">
      <template slot="fm-content" scope="x">
        <span class="value" :style="{color: x.fm.colour}">{{ format(x.fm.value) }}</span>
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

  .fm { cursor: pointer; }

  .chart {
    rect.fm {
      shape-rendering: crispEdges;
    }
  }

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

import BaseMixin from './mixins/Base.vue';
import ChartMixin from './mixins/Chart.vue';
import WithFMsMixin from './mixins/WithFMs';
import WithTooltipMixin from './mixins/WithTooltip';

import FMs from 'js/constants/financial-mechanisms.json5';


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
      inactive_opacity: .7,
    };
  },

  computed: {
    data() {
      // filter dataset by everything except fm
      const _filters = d3.keys(this.filters).filter( (f) => f != 'fm' );
      const dataset = this.filter(this.dataset, _filters);

      // base the data on the FM list from constants,
      // so even non-existing FMs get a 0 entry
      const fmdata = {}
      for (const fm in FMs) {
        fmdata[fm] = {
          'value': 0,
          'beneficiaries': d3.set(),
          'sectors': d3.set(),
        };
        Object.assign(fmdata[fm], FMs[fm]);
      }

      for (const d of dataset) {
        const id = slugify(d.fm),
              fm = fmdata[id],
              value = +d.allocation;

        // backend might send us empty data...
        if(value === 0) continue;

        fm.value += value;
        fm.sectors.add(d.sector);
        fm.beneficiaries.add(d.beneficiary);
      }

      return d3.values(fmdata);
    },
  },

  methods: {
    createTooltip() {
      const $this = this;

      let tip = d3.tip()
          .attr('class', 'd3-tip fms')
          .html(function(d) {
            return `<div class="title-container">
                      <span class="name">${d.name}</span>
                    </div>
                    <div>- ${$this.format(d.value)}  </div>
                    <div>- ${d.beneficiaries.size()} beneficiary states </div>
                    <div>- ${d.sectors.size()} priority sectors </div>
                    <span class="action">~Click to filter by financial mechanism</span>
            `;
          })
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

      const fms = chart
	    .selectAll("rect.fm")
            .data(this.data, (d) => d.id )

      const fentered = fms.enter().append("rect")
            .attr("class", (d) => "fm " + d.id)
            .attr("fill", (d) => d.colour )
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", 0)
            .attr("height", "100%")
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
            .on("mouseleave", this.tip.hide);

      /* // this is handled in tooltip already
      fentered
        .append("title").text( (d) => this.format(d.value) );
      fentered
        .append("desc").text( (d) => d.name );
      */

      fms.merge(fentered)
        .transition(t)
        .attr("width", (d) => x(d.value) );
    },

    handleFilterFm(val, old) {
      // transition the chart to disabled / selected.
      // (the legend is handled by vue.)
      const t = this.getTransition();

      this.chart.selectAll("rect.fm")
        .transition(t)
        .attr("fill", (d) => (
          this.isDisabledFm(d) ?
            colour2gray(d.colour, this.inactive_opacity) :
            d.colour
        ));
    },

    // for all other filters, re-render
    handleFilter() {
      this.render();
    },
  },
});

</script>
