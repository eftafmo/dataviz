<template>
  <div :class="classNames" class="funding-by-sector-chart">
    <embeddor
      :period="period"
      tag="sectors"
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
        <g class="chart">
          <g class="y-axis"></g>
        </g>
      </svg>
      <div class="funding-legend">
        <transition-group name="legend-item">
          <div v-for="item in data" :key="item.id" class="legend-item">
            <div
              class="legend-item-square"
              :style="{
                'background-color': item.sector.colour,
              }"
            ></div>
            <div class="legend-item-name">{{ item.sector.name }}</div>
          </div>
        </transition-group>
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
          allocation: item.allocation,
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
    yScale() {
      return d3
        .scaleLinear()
        .domain([0, this.maxAllocation])
        .range([this.height, 0])
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
      this.chart.attr(
        "transform",
        "translate(" + this.margin.left + "," + this.margin.top + ")"
      );

      this.renderYAxis();
      this.renderBars();

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
      const sectorsGroups = this.chart.selectAll("rect.sector").data(this.data);

      sectorsGroups
        .enter()
        .append("rect")
        .attr("class", "sector")
        .merge(sectorsGroups)
        .transition(t)
        .attr("x", (d) => this.xScale(d.id))
        .attr("y", (d) => this.yScale(d.allocation))
        .attr("width", this.xScale.bandwidth())
        .attr("height", (d) => this.height - this.yScale(d.allocation))
        .attr("fill", (d) => d.sector.colour)
        .attr("stroke", "none");
      sectorsGroups.exit().remove();
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
  // Hide these during transitions before we get to remove them
  .y-axis .domain {
    opacity: 0;
  }

  .sector:hover {
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

.legend-item-enter-active,
.legend-item-leave-active {
  transition: opacity 0.5s;
}
.legend-item-enter,
.legend-item-leave-to {
  opacity: 0;
}
.legend-item-move {
  transition: transform 0.5s;
}
.legend-item-leave-active {
  position: absolute;
}
</style>