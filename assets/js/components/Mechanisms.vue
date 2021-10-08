<template>
  <div :class="classNames">
    <embeddor
      :period="period"
      tag="mechanism"
      :svg-node="$refs.svgEl"
      :scale-download="2"
    />
    <slot v-if="!embedded" name="title"></slot>
    <dropdown
      v-if="rendered"
      filter="fm"
      title="No filter selected"
      :items="nonzero"
    ></dropdown>
    <svg
      ref="svgEl"
      :viewBox="`0 0 ${width} ${height + legendHeight}`"
      xmlns="http://www.w3.org/2000/svg"
      class="mechanism"
    >
      <chart-patterns :patterns="FM_ARRAY" />
      <g class="chart"></g>
      <template v-if="showTotals">
        <g v-for="(fm, index) in data" :key="fm.id">
          <text
            :x="(width / 2) * index + width / 4"
            :y="height + 10"
            :fill="isDisabledFm(fm) ? disabledColor : fm.color"
            dominant-baseline="hanging"
            text-anchor="middle"
            font-size="18"
            font-weight="bold"
          >
            {{ currency(fm.allocation) }}
          </text>
          <text
            :x="(width / 2) * index + width / 4"
            :y="height + legendHeight - 5"
            :fill="isDisabledFm(fm) ? disabledColor : '#000'"
            dominant-baseline="auto"
            text-anchor="middle"
            font-size="15"
          >
            {{ fm.name }}
          </text>
        </g>
      </template>
      <template v-else>
        <g v-for="(fm, index) in data" :key="`${fm.id}-legend-only`">
          <rect
            :x="index * (width / 4)"
            :y="height + legendHeight / 3"
            :fill="fm.stripesFill"
            :height="legendHeight / 4"
            :width="legendHeight / 4"
          />
          <text
            :x="index * (width / 4) + legendHeight / 4 + 10"
            :y="height + legendHeight / 3"
            :fill="isDisabledFm(fm) ? disabledColor : '#000'"
            dominant-baseline="hanging"
            text-anchor="start"
            font-size="15"
          >
            {{ fm.name }}
          </text>
        </g>
      </template>
    </svg>
  </div>
</template>

<script>
import * as d3 from "d3";
import d3tip from "d3-tip";
import { color2gray } from "@js/lib/util";

import Chart from "./Chart";

import WithFMsMixin from "./mixins/WithFMs";
import WithTooltipMixin from "./mixins/WithTooltip";
import Embeddor from "./includes/Embeddor";
import ChartPatterns from "./ChartPatterns";

export default {
  components: { ChartPatterns, Embeddor },
  extends: Chart,
  type: "fms",

  mixins: [WithFMsMixin, WithTooltipMixin],

  props: {
    disabledColor: {
      type: String,
      default: "#ccc",
    },
  },

  data() {
    return {
      width: 500,
      height: 30,
      legendHeight: 50,
      aggregate_by: [{ source: "fm", destination: "name" }],
      inactiveOpacity: 0.7,
      showTotals: true,
    };
  },

  computed: {
    data() {
      const out = [];
      let xOffset = 0;

      // base the data on the FM list from constants,
      // so even non-existing FMs get a 0 entry
      this.FM_ARRAY.forEach((fm) => {
        const item = this.aggregated[fm.name];
        const allocation = (item && item.allocation) || 0;

        out.push({
          ...fm,
          ...item,
          xOffset,
          allocation,
        });
        xOffset += allocation;
      });

      return out;
    },
    totalAllocation() {
      return this.data.reduce((total, item) => total + item.allocation, 0);
    },
    nonzero() {
      return this.data.filter((d) => d.allocation !== 0);
    },
    xScale() {
      return d3
        .scaleLinear()
        .rangeRound([0, this.width])
        .domain([0, this.totalAllocation]);
    },
  },

  created() {
    // don't filter by fm
    const idx = this.filter_by.indexOf("fm");

    if (idx !== -1) this.filter_by.splice(idx, 1);
  },

  methods: {
    renderChart() {
      const t = this.getTransition();
      const fmSlices = this.chart.selectAll("rect.fm-slice").data(this.data);
      fmSlices
        .enter()
        .append("rect")
        .attr("class", "fm-slice")
        .merge(fmSlices)
        .transition(t)
        .attr("x", (d) => this.xScale(d.xOffset))
        .attr("y", 0)
        .attr("width", (d) => this.xScale(d.allocation))
        .attr("height", this.height)
        .attr("fill", (d) =>
          this.isDisabledFm(d)
            ? color2gray(d.color, this.inactiveOpacity)
            : d.stripesFill
        );
      this.chart
        .selectAll("rect.fm-slice")
        .on("mouseenter", this.tip.show)
        .on("mouseleave", this.tip.hide)
        .on("click", (ev, d) => this.toggleFm(d));
    },
    tooltipTemplate(ev, d) {
      return (
        `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <div class="subtitle-container">
          <span class="donor-states">${d.donor_list}</span>
        </div>
        <ul>
          <li>${this.currency(d.allocation)}</li>
          <li>${this.getBeneficiaryCount(d.beneficiaries)} ` +
        this.singularize(
          `Beneficiary States`,
          this.getBeneficiaryCount(d.beneficiaries)
        ) +
        `</li>
          <li>${d.sectors.size} ` +
        this.singularize(`sectors`, d.sectors.size) +
        `</li>
          <li>${d.areas.size} ` +
        this.singularize(`programme areas`, d.areas.size) +
        `</li>
          <li>${d.programmes.size}  ` +
        this.singularize(`programmes`, d.programmes.size) +
        `</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
      `
      );
    },
    createTooltip() {
      this.tip = d3tip()
        .attr("class", "dataviz dataviz-tooltip fms")
        .html(this.tooltipTemplate)
        .direction("s")
        .offset([0, 0]);
      this.chart.call(this.tip);
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.fms {
  position: relative;

  .fms {
    text-align: center;
    padding-left: 0;
  }

  .chart {
    rect.fm-slice {
      cursor: pointer;
      shape-rendering: crispEdges;
    }
  }

  .legend {
    .fm {
      display: inline-block;
      border-right: 1px solid #ccc;
      padding: 0 2rem;

      @media (min-width: 400px) {
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
