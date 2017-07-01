<template>
<div class="overview-viz">
  <chart-container :width="width" :height="height" style="border: 1px dashed navy">
    <svg :viewBox="`0 0 ${width} ${height}`">
      <g class="chart" :transform="`translate(${margin + radius},${margin + radius})`">
        <g class="fms"></g>
        <g class="beneficiaries"></g>
        <g class="links"></g>
      </g>
    </svg>
  </chart-container>
</div>
</template>


<style lang="less">
.overview-viz {
  .chart {
    .fms, .beneficiaries  {
      fill: brown;
    }

    .links {
      fill: brown;
      fill-opacity: .75;
    }
  }
}
</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';

import xchord from 'js/lib/x-chord';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithFMsMixin, WithCountriesMixin,
  ],

  data() {
    return {
      width: 500,
      height: 500,

      padding: Math.PI / 2, // padding between groups, in radians
      itemPadding: Math.PI / 180, // padding between items, in radians

      inner_radius: .85, // percentage of outer radius
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

    arc() {
      return d3.arc()
        .outerRadius(this.radius)
        .innerRadius(this.innerRadius);
    },

    link() {
      return d3.ribbon()
        .radius(this.innerRadius);
    },

    chord() {
      return xchord()
        .padding(this.padding)
        .itemPadding(this.itemPadding);
    },

    filtered() {
      return this.filter(this.dataset);
    },
  },

  methods: {
    renderChart() {
      const matrix = [],
            dataset = this.aggregate(
              this.filtered, ['fm', 'beneficiary'], ['allocation'], false
            );

      // base the dataset on the constant list of FMs and beneficiaries,
      // to ensure 0-valued items exist regardless of filtering
      for (const fmid in this.FMS) {
        const fmname = this.FMS[fmid].name,
              fmdata = dataset[fmname],
              allocations = Array();

        matrix.push(allocations);

        if (fmdata === undefined) {
          allocations.length = d3.keys(this.BENEFICIARIES).length;
          allocations.fill(0);
          continue;
        }

        for (const bnfid in this.BENEFICIARIES) {
          const bnfdata = fmdata[bnfid];
          allocations.push(bnfdata !== undefined ? bnfdata.allocation : 0);
        }
      }

      const chords = this.chord(matrix);

      const fms = this.chart.select("g.fms")
                      .selectAll("path")
                      .data(chords.sources),
            beneficiaries = this.chart.select("g.beneficiaries")
                      .selectAll("path")
                      .data(chords.targets),
            links = this.chart.select("g.links")
                      .selectAll("path")
                      .data(chords);

      fms.enter()
        .append("path")
      .merge(fms)
        .attr("d", this.arc);

      beneficiaries.enter()
        .append("path")
      .merge(beneficiaries)
        .attr("d", this.arc);

      links.enter()
        .append("path")
      .merge(links)
        .attr("d", this.link);
    },
  },
});
</script>
