<template>
  <div :class="classNames">
    <embeddor
      :period="period"
      tag="global_goals"
      :svg-node="$refs.svgContainer"
      :scale-download="2"
    />
    <h2>Sustainable Development Goals</h2>
    <dropdown-filter
      filter="sdg_no"
      :items="allItems"
      title="Sustainable Development Goals"
    />
    <transition name="fade">
      <div v-if="currentGoal" class="current-goal">
        <img :src="currentGoal.imgURL" :alt="currentGoal.name" />
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
            :id="`stripes-pattern-sdg_no${patternData.id}`"
            :key="patternData.id"
            width="6"
            height="20"
            patternTransform="rotate(45 0 0)"
            patternUnits="userSpaceOnUse"
          >
            <rect
              width="100%"
              height="100%"
              :fill="patternData.color"
              fill-opacity="0.15"
            ></rect>
            <line
              x1="0"
              y1="0"
              x2="0"
              y2="100%"
              stroke-width="1"
              stroke-opacity="0.25"
              :stroke="patternData.color"
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
import allSDGs from "@js/constants/sdg.json5";
import Embeddor from "./includes/Embeddor";
import Chart from "./Chart";
import * as d3 from "d3";
import DropdownFilter from "./includes/DropdownFilter";

export default {
  name: "GlobalGoalsChart",
  components: { DropdownFilter, Embeddor },
  extends: Chart,
  type: "",

  data() {
    return {
      aggregate_by: ["sdg_no"],
      filter_by: ["fm", "beneficiary"],
      barHeight: 18,
      barPadding: 1.25,
      width: 500,
      disabledColor: "#9f9f9f",
      disabledFill: "url(#stripes-pattern-sdg_nodisabled)",
    };
  },
  computed: {
    allItems() {
      return allSDGs;
    },
    data() {
      return this.allItems.map((sdg, index) => {
        return {
          ...sdg,
          index,
          allocation: this.aggregated[sdg.id]?.allocation || 0,
          stripesFill: `url(#stripes-pattern-sdg_no${sdg.id})`,
          imgURL: this.getAssetUrl(`imgs/goals/${sdg.icon}`),
        };
      });
    },
    currentGoal() {
      if (!this.filters.sdg_no) return null;
      return this.data.find((item) => this.filters.sdg_no === item.id);
    },
    patternArray() {
      return [
        ...this.allItems,
        {
          id: "disabled",
          color: this.disabledColor,
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
        this.allItems.length *
        (this.barHeight + this.barHeight * this.barPadding)
      );
    },
  },
  methods: {
    toggleSDG(d) {
      this.filters.sdg_no = this.filters.sdg_no === d.id ? null : d.id;
    },
    isSelectedSDG(d) {
      return this.filters.sdg_no === d.id;
    },
    isDisabledSDG(d) {
      return this.filters.sdg_no && this.filters.sdg_no !== d.id;
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
        .on("click", (ev, d) => this.toggleSDG(d));
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
        .text((d) => d.id.toString());
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
          this.isDisabledSDG(d) ? this.disabledColor : d.color
        )
        .attr("stroke-width", 1)
        .attr("stroke-opacity", 0.25)
        .attr("fill", (d) =>
          this.isDisabledSDG(d) ? this.disabledFill : d.stripesFill
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
        .attr("font-weight", (d) => (this.isSelectedSDG(d) ? "bold" : "normal"))
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
        .attr("font-weight", (d) => (this.isSelectedSDG(d) ? "bold" : "normal"))
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

  img {
    max-width: 100%;
    max-height: 100%;
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