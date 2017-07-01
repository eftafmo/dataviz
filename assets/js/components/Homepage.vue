<template>
<div class="overview-viz">
  <chart-container :width="width" :height="height">
    <svg :viewBox="`0 0 ${width} ${height}`">
      <defs>
        <linearGradient id="link-gradient">
          <stop offset="10%"  stop-color="#ccc"/>
          <stop offset="90%" stop-color="#eee"/>
        </linearGradient>
      </defs>

      <g class="chart" :transform="`translate(${margin + radius},${margin + radius})`">
        <g class="fms"></g>
        <g class="beneficiaries"></g>
        <g class="links"></g>
      </g>
    </svg>

    <div v-if="hasData" class="info">
      <transition name="fade"><div class="heading" :key="changed">
        <p><span class="amount">{{ currency(aggregated.allocation) }}</span> spent on</p>
      </div></transition>
      <div class="data-wrapper"><transition name="fade"><ul class="data" :key="changed">
        <li class="programmes"><span class="amount">{{ number(aggregated.programmes.size()) }}</span> Programmes</li>
        <li class="projects"><span class="amount">{{ number(aggregated.project_count) }}</span> Projects</li>
      </ul></transition></div>
      <div class="ending">
        <p>to reduce social and economic disparities across Europe and to strenghten bilateral relations</p>
      </div>
    </div>

    <fm-legend :fms="FMS" class="legend clearfix">
      <template slot="fm-content" scope="x">
        <span :style="{backgroundColor: x.fm.colour}"></span>
        {{ x.fm.name }}
      </template>
    </fm-legend>
  </chart-container>
</div>
</template>


<style lang="less">
.overview-viz {
  .chart {
    .fms, .beneficiaries  {
      cursor: pointer;
      stroke-width: 1.34; // this should be equal to itemPadding

      path:hover {
        stroke-opacity: 1;
      }
    }

    .fms {
      stroke-opacity: .1;
    }

    .beneficiaries {
      fill: #ccc;
      stroke: #ccc;
      stroke-opacity: .5;
    }

    .links {
      fill: url("#link-gradient");
      fill-opacity: .75;

      .highlighted {
        fill-opacity: 1;
      }
      .non-highlighted {
        fill-opacity: .25;
      }
    }
  }

  .info {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    //background-color: rgba(200,200,200,.1);

    text-align: center;
    font-size: 2rem;

    p, ul, li {
      margin: 0;
    }

    span.amount {
      display: block;
      font-weight: bold;
    }

    & > div {
      position: absolute;
      width: 50%;
      left: 25%;
      pointer-events: initial;
    }

    .heading {
      top: 10%;
      font-size: 1.5em;

      /*
      .amount {
        font-size: 1.2em;
      }
      */
    }

    .data-wrapper {
      width: 40%;
      padding-bottom: 40%;
      left: 30%;
      top: 30%;
      //background-color: rgba(251, 251, 251, 0.8);
      background-image: linear-gradient(rgba(252, 252, 252, .75), rgba(227, 227, 227, .95));
      border: .2em solid white;
      border-radius: 50%;
    }

    .data {
      list-style-type: none;
      padding: 0;

      position: absolute;
      width: 100%;
      left: 50%;
      top: 50%;
      transform: translate(-50%,-50%);

      & > li:not(:last-child) {
        margin-bottom: .5em;
      }

      .programmes {
        font-size: 1.5em;
        line-height: 1.6em;

        .amount {
          font-size: 1.8em;
        }
      }

      .projects {
        font-size: 1em;

        .amount {
          font-size: 2em;
        }
      }
    }

    .ending {
      bottom: 0%;
      font-size: 1.2em;
    }
  }

  .legend {
    position: absolute;
    left: 0;
    top: 0;

    .fm span {
      width: 10px; height: 10px;
      display: inline-block;
    }
    li {
      list-style-type: none;
    }
  }

  .chart-container {
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 3rem;
    @media (min-width: 800px)and (max-width:1000px){
      width: 84%;
    }
    @media (min-width:1000px) {
      width: 60%;
    }
  }
}
</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';
import xchord from 'js/lib/x-chord';
import {slugify} from 'js/lib/util';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithFMsMixin, WithCountriesMixin
  ],

  data() {
    return {
      width: 500,
      height: 500,

      padding: Math.PI / 2, // padding between groups, in radians
      //itemPadding: 0,
      itemPadding: Math.PI / 180 / 3, // padding between items, in radians

      inner_radius: .85, // percentage of outer radius

      beneficiary_colour: "#ccc",
    };
  },

  computed: {
    margin() {
      // TODO: calculate maximum text width
      return 20;
    },

    radius() {
      return Math.min(this.width, this.height) / 2 - this.margin;
    },

    innerRadius() {
      return this.radius * this.inner_radius;
    },

    linksRadius() {
      // links should be exactly itemPadding apart
      return this.innerRadius - this.radius * this.itemPadding;
    },

    arc() {
      return d3.arc()
        .outerRadius(this.radius)
        .innerRadius(this.innerRadius);
    },

    link() {
      return d3.ribbon()
        .radius(this.linksRadius);
    },

    chord() {
      return xchord()
        .padding(this.padding)
        .itemPadding(this.itemPadding);
    },

    filtered() {
      return this.filter(this.dataset);
    },

    aggregated() {
      return this.aggregate(
        this.filtered,
        [],
        [
          'allocation', 'project_count',
          {source: 'programmes', type: Array},
        ],
        false
      );
    },

    // TODO: actually, these should come from the mixins
    // (and the constants should be arrays, and the objects pre-computed)
    FM_ARRAY() {
      return d3.values(this.FMS);
    },
    BENEFICIARY_ARRAY() {
      return d3.values(this.BENEFICIARIES);
    },

    data() {
      const matrix = [],
            dataset = this.aggregate(
              this.filtered, ['fm', 'beneficiary'], ['allocation'], false
            );

      // base the dataset on the constant list of FMs and beneficiaries,
      // to ensure 0-valued items exist regardless of filtering
      for (const fm of this.FM_ARRAY) {
        const fmdata = dataset[fm.name],
              allocations = Array();

        matrix.push(allocations);

        if (fmdata === undefined) {
          allocations.length = this.BENEFICIARY_ARRAY.length;
          allocations.fill(0);
          continue;
        }

        for (const bnf of this.BENEFICIARY_ARRAY) {
          const bnfdata = fmdata[bnf.id];
          allocations.push(bnfdata !== undefined ? bnfdata.allocation : 0);
        }
      }

      return this.chord(matrix);
    },
  },

  methods: {
    renderChart() {
      const $this = this,
            chords = this.data,
            t = this.getTransition();

      // avoid other transitions while this runs ¬
      t
        .on("start",
            () => this._transitioning = true )
        .on("end",
            () => this._transitioning = false )

      const fms = this.chart.select("g.fms")
                      .selectAll("path")
                      .data(chords.sources),
            beneficiaries = this.chart.select("g.beneficiaries")
                      .selectAll("path")
                      .data(chords.targets),
            links = this.chart.select("g.links")
                      .selectAll("path")
                      .data(chords);

      const fmcolour = (d) => this.FM_ARRAY[d.index].colour,
            extract_coords = (d) => ({
              startAngle: d.startAngle,
              endAngle: d.endAngle,
            }),
            extract_link_coords = (d) => ({
              source: extract_coords(d.source),
              target: extract_coords(d.target),
            });

      function mktweener(tweenfunc, coordsfunc) {
        return function(d) {
	  const interpolate = d3.interpolate(
	    this._prev, coordsfunc(d)
	  );
          this._prev = interpolate(0);

          return function(x) {
            return tweenfunc(interpolate(x));
          }
        }
      }

      const fentered = fms.enter()
        .append("path")
        .attr("fill", fmcolour)
        .attr("stroke", fmcolour)
        .on("click", function(d) {
          $this.toggleFm($this.FM_ARRAY[d.index]);
        })
        .on("mouseenter", this.mkhighlight("source"))
        .on("mouseleave", this.mkunhighlight("source"));

      const bentered = beneficiaries.enter()
        .append("path")
        .on("click", function(d) {
          $this.toggleBeneficiary($this.BENEFICIARY_ARRAY[d.index]);
        })
        .on("mouseenter", this.mkhighlight("target"))
        .on("mouseleave", this.mkunhighlight("target"));

      for (const sel of [fentered, bentered]) {
        sel
          .each(function(d){
            this._prev = extract_coords(d);
          })
          .attr("d", this.arc);
      }

      for (const sel of [fms, beneficiaries]) {
        sel
          .transition(t)
          .attrTween('d', mktweener(this.arc, extract_coords));
      }

      links.enter()
        .append("path")
        .each(function(d){
          this._prev = extract_link_coords(d);
        })
        .on("mouseenter", this.highlight)
        .on("mouseleave", this.unhighlight)
        .attr("d", this.link);

      links
        .transition(t)
        .attrTween('d', mktweener(this.link, extract_link_coords));
    },

    _highlight(index, yes) {
      // avoid funny race conditions ¬
      if(this._transitioning) return;

      //const t = this.getTransition(this.short_duration);

      const links = this.chart.select("g.links").selectAll("path");

      links.filter( (d, i) => i == index )
           .classed("highlighted", yes);
      links.filter( (d, i) => i != index)
           .classed("non-highlighted", yes);
    },

    _grouphighlight(index, type, yes) {
      // avoid funny race conditions ¬
      if(this._transitioning) return;

      //const t = this.getTransition(this.short_duration);

      const links = this.chart.select("g.links").selectAll("path");

      links.filter( (d) => d[type].index == index )
           .classed("highlighted", yes);
      links.filter( (d) => d[type].index != index )
           .classed("non-highlighted", yes);
    },

    highlight(d, i) {
      this._highlight(i, true);
    },

    unhighlight(d, i) {
      this._highlight(i, false);
    },

    mkhighlight(type) {
      const $this = this;
      return function(d, i) {
        $this._grouphighlight(i, type, true);
      };
    },

    mkunhighlight(type) {
      const $this = this;
      return function(d, i) {
        $this._grouphighlight(i, type, false);
      };
    }
  },
});
</script>
