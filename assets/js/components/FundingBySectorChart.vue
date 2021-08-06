<template>
  <div :class="classNames" class="funding-by-sector-chart">
    <embeddor :period="period" tag="sectors" />
    <div>
      <span>Funding by sectors in</span>
      <dropdown-filter
        filter="beneficiary"
        title="all Beneficiary States"
        :items="BENEFICIARY_ARRAY"
      />
    </div>
    <chart-container
      :width="svgWidth"
      :height="svgHeight"
      class="funding-chart-container"
    >
      <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`">
        <rect fill="#F5F5F5" :width="svgWidth" :height="svgHeight"></rect>
        <g class="chart"></g>
      </svg>
    </chart-container>
  </div>
</template>

<script>
import * as d3 from "d3";
import Chart from "./Chart";
import WithCountriesMixin from "./mixins/WithCountries";
import Embeddor from "./includes/Embeddor";
import DropdownFilter from "./includes/DropdownFilter";
import WithTooltipMixin from "./mixins/WithTooltip";
import WithSectors from "./mixins/WithSectors";
import { slugify } from "../lib/util";
import d3tip from "d3-tip";

export default {
  name: "FundingBySectorChart",
  components: { DropdownFilter, Embeddor },
  extends: Chart,
  type: "overview",

  mixins: [WithCountriesMixin, WithSectors, WithTooltipMixin],
  data() {
    return {
      aggregate_by: ["sector"],
      filter_by: ["beneficiary"],
      svgWidth: 560,
      svgHeight: 360,
      margin: {
        top: 30,
        right: 30,
        bottom: 30,
        left: 60,
      },
    };
  },
  computed: {
    data() {
      return Object.values(this.aggregated).map((item) => {
        const id = slugify(item.sector);
        return {
          id,
          sector: this.SECTORS[id],
          allocation: item.net_allocation,
        };
      });
    },
    width() {
      return this.svgWidth - this.margin.left - this.margin.right;
    },
    height() {
      return this.svgHeight - this.margin.top - this.margin.bottom;
    },
    maxAllocation() {
      return Math.max(...this.data.map((item) => item.allocation));
    },
    maxYValue() {
      const stepSize = Math.pow(10, 8);
      return Math.ceil(this.maxAllocation / stepSize) * stepSize;
    },
  },
  methods: {
    renderChart() {
      const t = this.getTransition();
      this.chart.selectAll("*").remove();
      this.chart.attr(
        "transform",
        "translate(" + this.margin.left + "," + this.margin.top + ")"
      );
      const xScale = d3
        .scaleBand()
        .range([0, this.width])
        .domain(this.data.map((item) => item.id))
        .padding(0);

      const yScale = d3
        .scaleLinear()
        .domain([0, this.maxAllocation])
        .range([this.height, 0])
        .nice();

      const yAxis = this.chart
        .append("g")
        .call(d3.axisLeft(yScale).tickFormat(this.shortCurrency));
      yAxis.select(".domain").remove();
      yAxis
        .selectAll(".tick line")
        .attr("x1", -5)
        .attr("x2", this.width + 5)
        .attr("stroke", "#DDDDDD");
      yAxis
        .selectAll(".tick text")
        .attr("font-weight", "bold")
        .attr("color", "#666666");

      const sectorsGroups = this.chart
        .selectAll("g.sector")
        .data(this.data, (d) => d.id)
        .enter()
        .append("g")
        .attr("class", "sector")
        .attr("transform-origin", `0 ${this.height}`)
        .attr("transform", "scale(1, 0)");
      sectorsGroups
        .append("rect")
        .attr("x", (d) => xScale(d.id))
        .attr("y", (d) => yScale(d.allocation))
        .attr("width", xScale.bandwidth())
        .attr("height", (d) => this.height - yScale(d.allocation))
        .attr("fill", (d) => d.sector.colour)
        .attr("stroke", "none")
        .on("mouseover", this.tip.show)
        .on("mouseout", this.tip.hide);

      sectorsGroups.transition(t).attr("transform", "scale(1, 1)");
    },
    tooltipTemplate(ev, d) {
      return `
        <div class="title-container">
          <span>${d.sector.name}</span>
        </div>
        <ul>
          <li>${this.currency(d.allocation)}</li>
        </ul>
      `;
    },
    createTooltip() {
      // add tooltip
      this.tip = d3tip()
        .attr("class", "dataviz-tooltip")
        .html(this.tooltipTemplate)
        .offset([-5, 0]);
      this.chart.call(this.tip);
    },
  },
};
</script>

<style lang="less">
.funding-chart-container {
  width: auto !important;
}

.funding-by-sector-chart {
  padding: 2rem 0;

  g.sector:hover {
    filter: drop-shadow(0px -2px 6px #3d3d3d);
  }
}
</style>