<template>
  <div :class="classNames">
    <embeddor
      :period="period"
      tag="global_goals"
      :svg-node="$refs.svgContainer"
      :scale-download="2"
    />
    <h2>Allocation by sector</h2>
    <dropdown-filter filter="sector" :items="dropDownItems" title="Sector" />
    <transition name="fade">
      <div
        v-if="currentGoal"
        class="current-goal"
        :style="{ 'background-color': currentGoal.color }"
      >
        <div class="current-goal-title">
          <div class="current-goal-index">
            {{ currentGoal.index + 1 }}
          </div>
          <div class="current-goal-name">
            {{ currentGoal.name }}
          </div>
        </div>
        <img :src="currentGoal.imgURL" alt="" />
      </div>
    </transition>
    <chart-container
      :width="width"
      :height="height"
      class="global-goals-chart-container"
    >
      <svg ref="svgContainer" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern
            v-for="patternData in patternArray"
            :id="`stripes-pattern-${patternData.id}`"
            :key="patternData.id"
            width="6"
            height="20"
            patternTransform="rotate(45 0 0)"
            patternUnits="userSpaceOnUse"
          >
            <rect
              width="100%"
              height="100%"
              :fill="patternData.colour"
              fill-opacity="0.15"
            ></rect>
            <line
              x1="0"
              y1="0"
              x2="0"
              y2="100%"
              stroke-width="1"
              stroke-opacity="0.25"
              :stroke="patternData.colour"
            />
          </pattern>
        </defs>
        <rect
          :width="width + 20"
          :height="height + 20"
          fill="white"
          x="-10"
          y="-10"
        ></rect>
        <g class="chart"></g>
      </svg>
    </chart-container>
  </div>
</template>

<script>
import Embeddor from "./includes/Embeddor";
import Chart from "./Chart";
import WithSectors from "./mixins/WithSectors";
import { slugify } from "../lib/util";
import * as d3 from "d3";
import DropdownFilter from "./includes/DropdownFilter";

export default {
  name: "GlobalGoalsChart",
  components: { DropdownFilter, Embeddor },
  extends: Chart,
  type: "",

  mixins: [WithSectors],
  data() {
    return {
      // TODO: Set to sectors for testing only.
      // TODO: NEEDS TO change after new data is available.
      aggregate_by: ["sector"],
      filter_by: ["fm", "beneficiary"],
      barHeight: 18,
      barPadding: 1.25,
      width: 500,
      disabledColor: "#9f9f9f",
      disabledFill: "url(#stripes-pattern-disabled-sector)",
    };
  },
  computed: {
    data() {
      return Object.entries(this.aggregated).map(([key, item], index) => {
        const id = slugify(key);
        return {
          id,
          index,
          name: key,
          color: this.sectorcolour(key),
          stripesFill: `url(#stripes-pattern-${id})`,
          imgURL: this.sectorUrl(key),
          ...item,
        };
      });
    },
    currentGoal() {
      if (!this.filters.sector) return null;
      const idToFind = slugify(this.filters.sector);
      return this.data.find((item) => idToFind === item.id);
    },
    dropDownItems() {
      return Array.from(new Set(this.dataset.map((item) => item.sector)));
    },
    patternArray() {
      return [
        ...this.SECTORS_ARRAY,
        {
          id: "disabled-sector",
          colour: this.disabledColor,
        },
      ];
    },
    maxAllocation() {
      return Math.max(...this.data.map((item) => item.allocation));
    },
    xScale() {
      // Leave room for the numbers on the right side
      const actualWidth = Math.floor((this.width - this.barHeight) * 0.7);
      return d3
        .scaleLinear()
        .rangeRound([0, actualWidth])
        .domain([0, this.maxAllocation])
        .nice();
    },
    height() {
      return (
        this.SECTORS_ARRAY.length *
        (this.barHeight + this.barHeight * this.barPadding)
      );
    },
  },
  methods: {
    toggleSector(d) {
      this.filters.sector = this.filters.sector === d.name ? null : d.name;
    },
    isSelectedSector(d) {
      return this.filters.sector === d.name;
    },
    isDisabledSector(d) {
      return this.filters.sector && this.filters.sector !== d.name;
    },
    yScale(d) {
      return d.index * (this.barHeight + this.barHeight * this.barPadding);
    },
    yScaleMiddle(d) {
      // Middle of the bar. Add 1 point extra to account for the stroke size
      return this.yScale(d) + Math.floor(this.barHeight / 2) + 1;
    },
    renderChart() {
      const t = this.getTransition();
      d3.select(this.$refs.svgContainer)
        .transition(t)
        .attr("viewBox", `0 0 ${this.width} ${this.height}`);

      this.updateSquares();
      this.updateBars();
      this.updateText();
      this.updateHoverBars();

      this.chart
        .selectAll("rect.hover-bar")
        .on("click", (ev, d) => this.toggleSector(d));
    },
    updateSquares() {
      const t = this.getTransition();
      const barSquares = this.chart
        .selectAll("rect.bar-square")
        .data(this.data);
      barSquares
        .enter()
        .append("rect")
        .attr("class", "bar-square")
        .merge(barSquares)
        .transition(t)
        .attr("x", 0)
        .attr("y", (d) => this.yScale(d))
        .attr("width", this.barHeight)
        .attr("height", this.barHeight)
        .attr("stroke", (d) => d.color)
        .attr("stroke-width", 1)
        .attr("fill", (d) => d.color);
      barSquares.exit().remove();

      const barSquaresText = this.chart
        .selectAll("text.index-label")
        .data(this.data);
      barSquaresText
        .enter()
        .append("text")
        .attr("class", "index-label")
        .merge(barSquaresText)
        .transition(t)
        .attr("x", this.barHeight / 2)
        .attr("y", (d) => this.yScaleMiddle(d))
        .attr("dominant-baseline", "middle")
        .attr("text-anchor", "middle")
        .attr("stroke", "none")
        .attr("fill", "white")
        .attr("font-weight", "bold")
        .text((d) => (d.index + 1).toString());
      barSquaresText.exit().remove();
    },
    updateBars() {
      const t = this.getTransition();
      const barGoals = this.chart.selectAll("rect.bar-goals").data(this.data);
      barGoals
        .enter()
        .append("rect")
        .attr("class", "bar-goals")
        .merge(barGoals)
        .transition(t)
        .attr("x", this.barHeight)
        .attr("y", (d) => this.yScale(d))
        .attr("width", (d) => this.barHeight + this.xScale(d.allocation))
        .attr("height", this.barHeight)
        .attr("stroke", (d) =>
          this.isDisabledSector(d) ? this.disabledColor : d.color
        )
        .attr("stroke-width", 1)
        .attr("stroke-opacity", 0.25)
        .attr("fill", (d) =>
          this.isDisabledSector(d) ? this.disabledFill : d.stripesFill
        );
      barGoals.exit().remove();
    },
    updateText() {
      const t = this.getTransition();
      const barLabels = this.chart.selectAll("text.goal-label").data(this.data);

      barLabels
        .enter()
        .append("text")
        .attr("class", "goal-label")
        .merge(barLabels)
        .transition(t)
        .attr("x", this.barHeight + 10)
        .attr("y", (d) => this.yScaleMiddle(d))
        .attr("font-size", "14px")
        .attr("font-weight", (d) =>
          this.isSelectedSector(d) ? "bold" : "normal"
        )
        .attr("dominant-baseline", "middle")
        .text((d) => d.name);
      barLabels.exit().remove();

      const goalValues = this.chart
        .selectAll("text.goal-values")
        .data(this.data);

      goalValues
        .enter()
        .append("text")
        .attr("class", "goal-values")
        .merge(goalValues)
        .transition(t)
        .attr("x", this.width - 10)
        .attr("y", (d) => this.yScaleMiddle(d))
        .attr("font-size", "14px")
        .attr("font-weight", (d) =>
          this.isSelectedSector(d) ? "bold" : "normal"
        )
        .attr("dominant-baseline", "middle")
        .attr("text-anchor", "end")
        .text((d) => this.currency(d.allocation));
      goalValues.exit().remove();
    },
    updateHoverBars() {
      const t = this.getTransition();
      const hoverBar = this.chart.selectAll("rect.hover-bar").data(this.data);
      hoverBar
        .enter()
        .append("rect")
        .attr("class", "hover-bar")
        .merge(hoverBar)
        .transition(t)
        .attr("x", 0)
        .attr("y", (d) => this.yScale(d))
        .attr("width", this.width)
        .attr("height", this.barHeight)
        .attr("stroke", (d) => d.color)
        .attr("stroke-width", 1)
        .attr("stroke-opacity", 0)
        .attr("fill", (d) => d.color)
        .attr("fill-opacity", 0);
      hoverBar.exit().remove();
    },
  },
};
</script>

<style lang="less">
.current-goal {
  width: 19rem;
  height: 19rem;
  margin: 5rem auto 7rem auto;
  padding: 1rem;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;

  .current-goal-title {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    color: white;
    font-weight: bold;
    width: 100%;

    .current-goal-index {
      font-size: 40px;
      margin-right: 1rem;
    }

    .current-goal-name {
      font-size: 16px;
      text-transform: uppercase;
    }
  }

  img {
    filter: invert(1);
    display: block;
    width: 12rem;
  }
}

.global-goals-chart-container {
  rect.hover-bar {
    cursor: pointer;

    &:hover {
      fill-opacity: 0.1;
      stroke-opacity: 0.1;
    }
  }
}
</style>