<template>
  <div :class="classNames" class="funding-by-sector-chart">
    <embeddor :period="period" tag="sectors" />
    <chart-container
      :width="svgWidth"
      :height="svgHeight"
      class="funding-chart-container"
    >
      <svg
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect fill="#F5F5F5" :width="svgWidth" :height="svgHeight"></rect>
        <image
          v-if="filters.beneficiary"
          x="20"
          y="20"
          width="36"
          height="26"
          :href="get_flag_url(filters.beneficiary)"
        ></image>
        <text
          :x="filters.beneficiary ? 70 : 20"
          y="20"
          font-size="26"
          dominant-baseline="hanging"
        >
          <template v-if="!filters.beneficiary">
            All beneficiary states
          </template>
          <template v-else>
            {{ get_country_name(filters.beneficiary) }}
          </template>
          {{ period }}
        </text>
        <g class="chart"></g>
      </svg>
      <div class="funding-legend">
        <div v-for="item in data" :key="item.id" class="legend-item">
          <div
            class="legend-item-square"
            :style="{
              'background-color': item.sector.colour,
            }"
          ></div>
          <div class="legend-item-name">{{ item.sector.name }}</div>
        </div>
      </div>
    </chart-container>
  </div>
</template>

<script>
import * as d3 from "d3";
import Chart from "./Chart";
import WithCountriesMixin from "./mixins/WithCountries";
import Embeddor from "./includes/Embeddor";
import WithTooltipMixin from "./mixins/WithTooltip";
import WithSectors from "./mixins/WithSectors";
import { slugify } from "../lib/util";
import d3tip from "d3-tip";

export default {
  name: "FundingBySectorChart",
  components: { Embeddor },
  extends: Chart,
  type: "",

  mixins: [WithCountriesMixin, WithSectors, WithTooltipMixin],
  data() {
    return {
      aggregate_by: ["sector"],
      filter_by: ["beneficiary"],
      svgWidth: 560,
      svgHeight: 360,
      margin: {
        top: 70,
        right: 30,
        bottom: 20,
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
  g.sector:hover {
    filter: drop-shadow(0px -2px 6px #3d3d3d);
  }

  .funding-legend {
    border: 4px solid #f5f5f5;
    padding: 3rem;

    .legend-item {
      display: flex;
      align-items: center;
      font-size: 1.6rem;
      line-height: 1;
    }

    .legend-item + .legend-item {
      margin-top: 1.5rem;
    }

    .legend-item-square {
      display: block;
      min-width: 1.8rem;
      max-width: 1.8rem;
      max-height: 1.8rem;
      min-height: 1.8rem;
      margin-right: 1.2rem;
    }
  }

  @media (max-width: 600px) {
    .funding-legend {
      padding: 1rem;
    }
  }
}
</style>