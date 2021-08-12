<template>
  <div :class="classNames" class="funding-by-period-chart">
    <embeddor :period="period" tag="beneficiary_states" />
    <chart-container
      :width="svgWidth"
      :height="svgHeight"
      class="funding-period-chart-container"
    >
      <svg
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        xmlns="http://www.w3.org/2000/svg"
      >
        <chart-patterns />
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
        </text>
        <g class="chart">
          <g class="y-axis"></g>
          <g class="x-axis"></g>
        </g>
      </svg>
    </chart-container>
  </div>
</template>

<script>
import Embeddor from "./includes/Embeddor";
import Chart from "./Chart";
import WithCountriesMixin from "./mixins/WithCountries";
import WithFMs from "./mixins/WithFMs";
import * as d3 from "d3";
import WithTooltip from "./mixins/WithTooltip";
import d3tip from "d3-tip";
import ChartPatterns from "./ChartPatterns";

export default {
  name: "FundingByPeriodChart",
  components: { ChartPatterns, Embeddor },
  extends: Chart,
  type: "",

  mixins: [WithCountriesMixin, WithFMs, WithTooltip],
  data() {
    return {
      aggregate_by: ["period", "fm"],
      filter_by: ["fm", "beneficiary"],
      svgWidth: 600,
      svgHeight: 600,
      margin: {
        top: 70,
        right: 30,
        bottom: 60,
        left: 60,
      },
    };
  },
  computed: {
    aggregatedByPeriod() {
      // TODO: testing only
      const x = this.aggregate(this.filtered, ["period"], this.aggregate_on);
      return {
        "2004-2009": x["2009-2014"],
        "2009-2014": x["2009-2014"],
        "2014-2021": x["2009-2014"],
      };
    },
    aggregatedByPeriodAndFm() {
      // TODO: testing only
      return {
        "2004-2009": this.aggregated["2009-2014"],
        "2009-2014": this.aggregated["2009-2014"],
        "2014-2021": this.aggregated["2009-2014"],
      };
    },
    data() {
      const result = [];
      Object.entries(this.aggregatedByPeriodAndFm).forEach(
        ([period, periodData]) => {
          let yOffset = 0;
          this.FM_ARRAY.forEach((fm) => {
            const details = periodData[fm.name];
            // These can be zero for specific beneficiaries. However we still
            // need to draw them in order for them to be animated when filters change.
            const net_allocation = (details && details.net_allocation) || 0;

            result.push({
              id: `${period}-${fm.id}`,
              fmId: fm.id,
              net_allocation,
              drawnAllocation: yOffset + net_allocation,
              period,
              details,
              stripesFill: fm.stripesFill,
            });
            // Keep track of the offset for this period, as the bars
            // as stacked on top of each other.
            yOffset += net_allocation;
          });
        }
      );
      return result;
    },
    totalData() {
      return Object.entries(this.aggregatedByPeriod).map(
        ([period, periodData]) => {
          return {
            ...periodData,
            id: period,
            period: period,
          };
        }
      );
    },
    width() {
      return this.svgWidth - this.margin.left - this.margin.right;
    },
    height() {
      return this.svgHeight - this.margin.top - this.margin.bottom;
    },
    maxAllocation() {
      return Math.max(...this.data.map((item) => item.drawnAllocation));
    },
    xScale() {
      return d3
        .scaleBand()
        .range([0, this.width])
        .domain(this.data.map((item) => item.period))
        .padding(0.25);
    },
    yScale() {
      return d3
        .scaleLinear()
        .domain([0, this.maxAllocation])
        .range([this.height, 0])
        .nice();
    },
  },
  methods: {
    renderChart() {
      this.chart.attr(
        "transform",
        "translate(" + this.margin.left + "," + this.margin.top + ")"
      );
      this.updateChart();
      this.chart
        .selectAll("rect.period-bar")
        .on("mouseover", this.tip.show)
        .on("mouseout", this.tip.hide);
    },
    updateChart() {
      // Order IS important, the X axis should be drawn over
      // the 0 line over the Y axis.
      this.renderYAxis();
      this.renderBars();
      this.renderXAxis();
    },
    renderXAxis() {
      const t = this.getTransition();

      const xAxis = this.chart
        .select(".x-axis")
        .attr("transform", "translate(0," + this.height + ")")
        .transition(t)
        .call(d3.axisBottom(this.xScale));
      xAxis.select(".domain").attr("fill", "#DF514E").attr("stroke", "#DF514E");
      xAxis.selectAll(".tick line").remove();
      xAxis
        .selectAll(".tick text")
        .attr("dominant-baseline", "middle")
        .attr("font-size", "24px")
        .attr("font-weight", "bold")
        .attr("color", "#666666");
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
        .attr("x2", this.width)
        .attr("stroke", "#DDDDDD");
      yAxis
        .selectAll(".tick text")
        .attr("font-weight", "bold")
        .attr("color", "#666666");
    },
    renderBars() {
      const t = this.getTransition();
      const fmBars = this.chart.selectAll("rect.fm-bar").data(this.data);
      fmBars
        .enter()
        .append("rect")
        .attr("class", "fm-bar")
        .merge(fmBars)
        .transition(t)
        .attr("x", (d) => this.xScale(d.period))
        .attr("y", (d) => this.yScale(d.drawnAllocation))
        .attr("width", this.xScale.bandwidth())
        .attr("height", (d) => this.height - this.yScale(d.net_allocation))
        .attr("stroke", "none")
        .attr("fill", (d) => d.stripesFill);

      const periodBars = this.chart
        .selectAll("rect.period-bar")
        .data(this.totalData);
      periodBars
        .enter()
        .append("rect")
        .attr("class", "period-bar")
        .merge(periodBars)
        .transition(t)
        .attr("x", (d) => this.xScale(d.period))
        .attr("y", (d) => this.yScale(d.net_allocation))
        .attr("width", this.xScale.bandwidth())
        .attr("height", (d) => this.height - this.yScale(d.net_allocation))
        .attr("fill", "transparent")
        .attr("opacity", 0);
    },
    tooltipTemplate(ev, d) {
      return `
        <div class="title-container">
          <span>Financial Mechanism: ${d.period}</span>
        </div>
        <div class="title-container legend-container">
          ${this.tooltipLegendTemplate(d)}
        </div>
        <ul class="muted">
          <li>
            ${d.beneficiaries.size}
            ${this.singularize("beneficiary states", d.beneficiaries.size)}
          </li>
          <li>
            ${d.sectors.size}
            ${this.singularize("sectors", d.sectors.size)}
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
    tooltipLegendTemplate(d) {
      const data = this.aggregatedByPeriodAndFm[d.period];

      return this.FM_ARRAY.map((fm) => {
        const allocation = (data[fm.name] && data[fm.name].net_allocation) || 0;
        return `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">
            <rect width="12" height="12" fill="${fm.stripesFill}">
          </svg>
          <span>
             ${fm.name}
          </span>
          <span class="muted">
            ${this.currency(allocation)}
          </span>
        `;
      }).join("");
    },
    createTooltip() {
      // add tooltip
      this.tip = d3tip()
        .attr("class", "dataviz-tooltip")
        .html(this.tooltipTemplate)
        .offset([30, 0]);
      this.chart.call(this.tip);
    },
  },
};
</script>


<style lang="less">
.funding-period-chart-container {
  width: auto !important;
}

.funding-by-period-chart {
  // Hide these during transitions before we get to remove them
  .y-axis .domain {
    opacity: 0;
  }
}
</style>