import * as d3 from "d3";
import debounce from "lodash.debounce";

import ChartContainer from "../includes/ChartContainer";

export default {
  components: {
    "chart-container": ChartContainer,
  },

  data: function () {
    return {
      // these are to be recomputed on any layout changes.
      // setting them explicitly to null, so things fail with a bang
      // if initialised too early
      chartWidth: null,
      chartHeight: null,
      fontSize: null,

      // timings for debouncing render functions (in milliseconds)
      renderWait: {
        min: 17, // ~ 1 frame @ 60fps
        max: 100,
      },
    };
  },

  created() {
    // replace this.render() with a debounced version
    this.render = debounce(this.render, this.renderWait.min, {
      maxWait: this.renderWait.max,
    });

    // do that to computeDimensions as well, because why not
    // (but allow it to be delayed indefinitely)
    this.computeDimensions = debounce(
      this.computeDimensions,
      this.renderWait.min,
    );
  },

  mounted() {
    const el = d3.select(this.$el);
    if (!el || !el.select) return;

    this.chart = el.select(".chart");
    const chart = this.chart.node();
    this.svg = chart.ownerSVGElement ? chart.ownerSVGElement : chart;

    this.computeDimensions();
    window.addEventListener("resize", this.computeDimensions);
  },

  beforeUnmount() {
    window.removeEventListener("resize", this.computeDimensions);
  },

  methods: {
    computeDimensions(event) {
      const bounds = this.svg.getBoundingClientRect();

      this.chartWidth = bounds.width;
      this.chartHeight = bounds.height;

      this.fontSize = parseFloat(getComputedStyle(this.svg).fontSize);
    },

    // NOTE: nobody calls this by default.
    // the initial run should be wrapped under nextTick:
    // ```
    // this.$nextTick(this.render);
    // ```
    // to allow computeDimensions() to do its work
    render() {
      throw new Error("Not implemented");
    },
  },
};
