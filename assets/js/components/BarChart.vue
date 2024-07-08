<template>
  <div :class="classNames">
    <embeddor
      :period="period"
      :tag="embedTag"
      :svg-node="$refs.svgContainer"
      :scale-download="2"
    />
    <h2>{{ title }}</h2>
    <dropdown-filter
      :filter="mainFilter"
      :items="data"
      :title="dropDownTitle"
    />
    <slot name="before-chart"></slot>
    <chart-container
      :width="width"
      :height="height"
      class="stripped-chart-container"
    >
      <svg ref="svgContainer" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern
            v-for="patternData in patternArray"
            :id="`stripes-pattern-${mainFilter}${patternData.id}`"
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
        <g class="chart"></g>
      </svg>
    </chart-container>
  </div>
</template>

<script>
import Chart from "./Chart";
import Embeddor from "./includes/Embeddor";
import DropdownFilter from "./includes/DropdownFilter";
import * as d3 from "d3";
import d3tip from "d3-tip";
import WithTooltip from "./mixins/WithTooltip";

export default {
  name: "BarChart",
  components: { DropdownFilter, Embeddor },
  extends: Chart,
  mixins: [WithTooltip],
  props: {
    mainFilter: {
      type: String,
      required: true,
    },
    allItems: {
      type: Array,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    dropDownTitle: {
      type: String,
      required: true,
    },
    embedTag: {
      type: String,
      required: true,
    },
    showId: {
      type: Boolean,
      default: false,
    },
    hideZero: {
      type: Boolean,
      required: false,
      default: false,
    },
    allocationField: {
      type: String,
      required: false,
      default: "allocation",
    },
    allocationType: {
      type: String,
      required: false,
      default: "gross",
    },
  },
  data() {
    return {
      aggregate_by: null,
      width: 500,
      barHeight: 18,
      barPadding: 0.9,
      textColor: "#444",
      disabledColor: "#9f9f9f",
      disabledTextColor: "#ccc",
    };
  },
  computed: {
    data() {
      return this.allItems
        .filter((item) => !this.hideZero || this.getAllocation(item.id) > 0)
        .map((item, index) => {
          const d = this.aggregated[item.id];
          return {
            ...d,
            ...item,
            index,
            allocation: this.getAllocation(item.id),
          };
        });
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
      // Make sure the max allocation is always > 0. Otherwise all
      // bars in the bar chart will have full width, even thought they
      // are all 0. This makes the chart really confusing otherwise.
      return Math.max(...this.data.map((item) => item.allocation)) || 1;
    },
    height() {
      return (
        this.allItems.length *
        (this.barHeight + this.barHeight * this.barPadding)
      );
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
  },
  created() {
    this.aggregate_by = [this.mainFilter];
    // Don't filter data by the pivot key, as we always want to display all
    // items.
    this.filter_by = this.filter_by.filter((f) => f !== this.mainFilter);
  },
  methods: {
    getAllocation(id) {
      return this.aggregated[id]
        ? this.aggregated[id][this.allocationField]
        : 0;
    },
    getStripeUrl(id) {
      return `url(#stripes-pattern-${this.mainFilter}${id})`;
    },
    toggleFilter(d) {
      this.filters[this.mainFilter] =
        this.filters[this.mainFilter] === d.id.toString()
          ? null
          : d.id.toString();
    },
    isSelected(d) {
      return this.filters[this.mainFilter] === d.id.toString();
    },
    isDisabled(d) {
      return (
        this.filters[this.mainFilter] &&
        this.filters[this.mainFilter] !== d.id.toString()
      );
    },
    renderChart() {
      const t = this.getTransition();
      d3.select(this.$refs.svgContainer)
        .transition(t)
        .attr("viewBox", `0 0 ${this.width} ${this.height}`);

      this.updateSquares();
      if (this.showId) this.updateSquareId();
      this.updateBars();
      this.updateText();
      this.updateHoverBars();

      this.chart
        .selectAll("rect.hover-bar")
        .on("click", (ev, d) => this.toggleFilter(d))
        .on("mouseover", this.tip.show)
        .on("mouseout", this.tip.hide);
    },
    yScale(d) {
      return d.index * (this.barHeight + this.barHeight * this.barPadding);
    },
    yScaleMiddle(d) {
      // Middle of the bar. Add 1 point extra to account for the stroke size
      return this.yScale(d) + Math.floor(this.barHeight / 2) + 1;
    },
    updateSquares() {
      const t = this.getTransition();
      const barSquares = this.chart
        .selectAll("rect.bar-square")
        .data(this.data, (d) => d.id);
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
        .attr("opacity", (d) => (this.isDisabled(d) ? 0.5 : 1))
        .attr("fill", (d) => d.color);
      barSquares.exit().remove();
    },
    updateSquareId() {
      const t = this.getTransition();
      const barSquaresText = this.chart
        .selectAll("text.id-label")
        .data(this.data, (d) => d.id);
      barSquaresText
        .enter()
        .append("text")
        .attr("class", "id-label")
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
      const bars = this.chart
        .selectAll("rect.bar-item")
        .data(this.data, (d) => d.id);
      bars
        .enter()
        .append("rect")
        .attr("class", "bar-item")
        .merge(bars)
        .transition(t)
        .attr("x", 0)
        .attr("y", (d) => this.yScale(d))
        .attr("width", (d) => this.barHeight + this.xScale(d.allocation))
        .attr("height", this.barHeight)
        .attr("stroke", (d) =>
          this.isDisabled(d) ? this.disabledColor : d.color,
        )
        .attr("stroke-width", 1)
        .attr("stroke-opacity", 0.25)
        .attr("fill", (d) =>
          this.getStripeUrl(this.isDisabled(d) ? "disabled" : d.id),
        );
      bars.exit().remove();
    },

    updateText() {
      const t = this.getTransition();
      const barLabels = this.chart
        .selectAll("text.bar-label")
        .data(this.data, (d) => d.id);

      barLabels
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .merge(barLabels)
        .transition(t)
        .attr("x", this.barHeight + 10)
        .attr("y", (d) => this.yScaleMiddle(d))
        .attr("fill", (d) =>
          this.isDisabled(d) ? this.disabledTextColor : this.textColor,
        )
        .attr("font-size", "14px")
        .attr("font-weight", (d) => (this.isSelected(d) ? "bold" : "normal"))
        .attr("dominant-baseline", "middle")
        .text((d) => d.name);
      barLabels.exit().remove();

      const barValues = this.chart
        .selectAll("text.bar-values")
        .data(this.data, (d) => d.id);

      barValues
        .enter()
        .append("text")
        .attr("class", "bar-values")
        .merge(barValues)
        .transition(t)
        .attr("x", this.width - 10)
        .attr("y", (d) => this.yScaleMiddle(d))
        .attr("fill", (d) =>
          this.isDisabled(d) ? this.disabledTextColor : this.textColor,
        )
        .attr("font-size", "14px")
        .attr("font-weight", (d) => (this.isSelected(d) ? "bold" : "normal"))
        .attr("dominant-baseline", "middle")
        .attr("text-anchor", "end")
        .text((d) => this.currency(d.allocation));
      barValues.exit().remove();
    },

    updateHoverBars() {
      const t = this.getTransition();
      const hoverBar = this.chart
        .selectAll("rect.hover-bar")
        .data(this.data, (d) => d.id);
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
    tooltipTemplate(ev, d) {
      return `
        <div class="title-container">
          <span>${d.name}</span>
        </div>
        <ul>
          <li>
            ${this.currency(d.allocation)}
            ${this.allocationType} allocation
          </li>
          <li>
            ${this.getBeneficiaryCount(d.beneficiaries)}
            ${this.singularize(
              "Beneficiary States",
              this.getBeneficiaryCount(d.beneficiaries),
            )}
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
.stripped-chart-container {
  rect.hover-bar {
    cursor: pointer;

    &:hover {
      fill-opacity: 0.1;
      stroke-opacity: 0.1;
    }
  }
}
</style>