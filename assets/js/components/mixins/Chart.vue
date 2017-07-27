<script>
import * as d3 from 'd3';
import debounce from 'lodash.debounce';

import Component from './Component';

import Dropdown from '../includes/DropdownFilter';
import ChartContainer from '../includes/ChartContainer';

export default {
  extends: Component,

  components: {
    'dropdown': Dropdown,
    'chart-container': ChartContainer,
  },

  data: function() {
    return {
      rendered: false,

      // these are to be recomputed on any layout changes.
      // setting them explicitly to null, so things fail with a bang
      // if initialized too early
      svgWidth: null,
      fontSize: null,

      // these need to be synced with each component's css
      // TODO: load them from a common json / less-file?
      // default transition duration
      duration: 500,
      // alternate
      short_duration: 250,

      // timings for debouncing render functions (in milliseconds)
      renderWait: {
        min: 17,
        max: 100,
      },
    };
  },

  mounted() {
    this.chart = d3.select(this.$el).select('.chart');

    this.computeDimensions();
    window.addEventListener('resize', this.computeDimensions);
  },

  methods: {
    main() {
      // we need to do the rendering during next tick only,
      // to allow computeDimensions() to do its work
      this.$nextTick(this.render);
    },

    render(initial) {
      if (initial) this.rendered = false;

      let renderer = this._renderer;
      if (renderer === undefined)
        renderer = this._renderer = debounce(
          () => {
            this.renderChart();
            this.rendered = true;
          },
          this.renderWait.min, {maxWait: this.renderWait.max}
        );

      renderer();
    },

    renderChart() {
      throw new Error("Not implemented");
    },

    computeDimensions(event) {
      const chart = this.chart.node(),
            svg = chart.ownerSVGElement ? chart.ownerSVGElement : chart;

      this.svgWidth = svg.getBoundingClientRect().width;
      this.fontSize = parseFloat(getComputedStyle(svg).fontSize);
    },

    getTransition(duration) {
      // returns a transition that has 0 duration during first render
      if (!this.rendered) duration = 0
      else if (duration === undefined) duration = this.duration;

      return d3.transition()
               .duration(duration);
    },

    // filters should re-render by default, unless specifically handled
    handleFilter() {
      this.render();
    },
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.computeDimensions);
  },
};
</script>
