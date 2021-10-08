<template>
  <div :class="classNames" class="funding-by-sector-chart">
    <embeddor
      :period="period"
      tag="funding_by_sector_chart"
      :svg-node="$refs.svgEl"
      :scale-download="2"
    />
    <chart-container
      :width="svgWidth"
      :height="svgHeight"
      class="funding-chart-container"
    >
      <svg
        ref="svgEl"
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect
          :fill="bgColor"
          :width="svgWidth"
          :height="barChartHeight + margin.top + margin.bottom"
        ></rect>
        <image
          v-if="filters.beneficiary"
          x="20"
          y="20"
          width="36"
          height="26"
          :href="get_flag(filters.beneficiary)"
        ></image>
        <text
          :x="filters.beneficiary ? 70 : 20"
          y="20"
          font-size="26"
          dominant-baseline="hanging"
        >
          <template v-if="!filters.beneficiary">
            All Beneficiary States
          </template>
          <template v-else>
            {{ get_country_name(filters.beneficiary) }}
          </template>
          {{ period }}
        </text>
        <g class="chart">
          <g class="y-axis"></g>
          <g class="bar-chart"></g>
        </g>
      </svg>
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
      aggregate_by: ["period", "sector"],
      filter_by: ["beneficiary"],
      svgWidth: 560,
      barChartHeight: 250,
      margin: {
        top: 70,
        right: 30,
        bottom: 20,
        left: 60,
      },
      legendPadding: 10,
      legendSquareSize: 16,
      legendItemHeight: 36,
      legendBorder: 4,
      bgColor: "#F5F5F5",
    };
  },
  computed: {
    data() {
      const periodData = this.aggregated[this.period];
      if (!periodData) return [];

      return Object.values(periodData)
        .map((item) => {
          const id = slugify(item.sector);
          return {
            ...item,
            id,
            sector: this.SECTORS[id],
          };
        })
        .sort((a, b) => a.sector.sortOrder - b.sector.sortOrder);
    },
    width() {
      return this.svgWidth - this.margin.left - this.margin.right;
    },
    legendHeight() {
      return this.data.length * this.legendItemHeight + this.legendPadding * 2;
    },
    svgHeight() {
      return (
        this.barChartHeight +
        this.margin.top +
        this.margin.bottom +
        this.legendHeight
      );
    },
    maxAllocation() {
      return Math.max(...this.data.map((item) => item.allocation));
    },
    yScale() {
      return d3
        .scaleLinear()
        .domain([0, this.maxAllocation])
        .range([this.barChartHeight, 0])
        .nice();
    },
    xScale() {
      return d3
        .scaleBand()
        .range([0, this.width])
        .domain(this.data.map((item) => item.id))
        .padding(0);
    },
  },
  methods: {
    renderChart() {
      this.chart
        .selectAll("g.bar-chart, g.y-axis")
        .attr(
          "transform",
          "translate(" + this.margin.left + "," + this.margin.top + ")"
        );

      this.renderYAxis();
      this.renderBars();
      this.renderLegend();

      this.chart
        .selectAll("rect.sector")
        .on("mouseover", this.tip.show)
        .on("mouseout", this.tip.hide);
    },
    renderYAxis() {
      const t = this.getTransition();

      const yAxis = this.chart
        .select(".y-axis")
        .transition(t)
        .call(d3.axisLeft(this.yScale).tickFormat(this.shortCurrency));

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
    },
    renderBars() {
      const t = this.getTransition();
      const sectorsGroups = this.chart
        .select("g.bar-chart")
        .selectAll("rect.sector")
        .data(this.data);

      sectorsGroups
        .enter()
        .append("rect")
        .attr("class", "sector")
        .merge(sectorsGroups)
        .transition(t)
        .attr("x", (d) => this.xScale(d.id))
        .attr("y", (d) => this.yScale(d.allocation))
        .attr("width", this.xScale.bandwidth())
        .attr("height", (d) => this.barChartHeight - this.yScale(d.allocation))
        .attr("fill", (d) => d.sector.color)
        .attr("stroke", "none");
      sectorsGroups.exit().remove();
    },
    renderLegend() {
      const t = this.getTransition();
      const xOffset = this.legendBorder / 2;
      const yOffset =
        this.barChartHeight + this.margin.top + this.margin.bottom;
      const legendBg = this.chart
        .selectAll("rect.legend-bg")
        .data([this.data.length]);

      legendBg
        .enter()
        .append("rect")
        .attr("class", "legend-bg")
        .merge(legendBg)
        .attr("x", xOffset)
        .attr("y", yOffset)
        .attr("width", this.svgWidth - this.legendBorder)
        .attr("height", this.legendHeight - this.legendBorder)
        .attr("fill", "white")
        .attr("stroke", this.bgColor)
        .attr("stroke-width", this.legendBorder);

      const legendSquare = this.chart
        .selectAll("rect.legend-square")
        .data(this.data);
      legendSquare
        .enter()
        .append("rect")
        .attr("class", "legend-square")
        .merge(legendSquare)
        .transition(t)
        .attr("x", xOffset + this.legendPadding)
        .attr(
          "y",
          (d, i) => yOffset + i * this.legendItemHeight + this.legendPadding
        )
        .attr("width", this.legendSquareSize)
        .attr("height", this.legendSquareSize)
        .attr("fill", (d) => d.sector.color);
      legendSquare.exit().remove();

      const legendLabels = this.chart
        .selectAll("text.legend-text")
        .data(this.data);
      legendLabels
        .enter()
        .append("text")
        .attr("class", "legend-text")
        .merge(legendLabels)
        .transition(t)
        .attr(
          "x",
          xOffset +
            this.legendPadding +
            this.legendSquareSize +
            this.legendPadding
        )
        .attr(
          "y",
          (d, i) =>
            yOffset +
            i * this.legendItemHeight +
            this.legendPadding +
            this.legendSquareSize / 2 +
            1
        )
        .attr("line-height", 1)
        .attr("font-size", 16)
        .attr("dominant-baseline", "middle")
        .text((d) => d.sector.name);
      legendLabels.exit().remove();
    },
    tooltipTemplate(ev, d) {
      return `
        <div class="title-container">
          <span>${d.sector.name}</span>
        </div>
        <ul>
          <li>${this.currency(d.allocation)}</li>
          <li>
            ${this.getBeneficiaryCount(d.beneficiaries)}
            ${this.singularize(
              "Beneficiary States",
              this.getBeneficiaryCount(d.beneficiaries)
            )}
          </li>
          <li>
            ${d.areas.size}
            ${this.singularize("programme areas", d.areas.size)}
          </li>
          <li>
            ${d.programmes.size}
            ${this.singularize("programmes", d.programmes.size)}
          </li>
        </ul>
      `;
    },
    createTooltip() {
      // add tooltip
      this.tip = d3tip()
        .attr("class", "dataviz dataviz-tooltip")
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
  // Hide these during transitions before we get to remove them
  .y-axis .domain {
    opacity: 0;
  }

  .sector:hover {
    filter: drop-shadow(0px -2px 6px #3d3d3d);
  }
}
</style>