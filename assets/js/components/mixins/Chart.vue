<script>
import * as d3 from 'd3';
import Dropdown from '../includes/DropdownFilter';
import ChartContainer from '../includes/ChartContainer';

export default {
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
      // opacity of filtered-out items
      inactive_opacity: .7,
    }
  },

  mounted() {
    this.chart = d3.select(this.$el).select('.chart');
    this.legend = d3.select(this.$el).select('.legend');

    this.computeDimensions();
    window.addEventListener('resize', this.computeDimensions);
  },

  methods: {
    main() {
      // we need to do the rendering during next tick only,
      // to allow computeDimensions() to do its work
      this.$nextTick(this.render);
    },
    render() {
      this.renderChart();
      this.renderLegend();
      this.rendered = true;
    },
    renderChart() {
      throw "Not implemented";
    },
    renderLegend() {
      // don't throw, not all visualisations implement this
      return;
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
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.computeDimensions);
  },
};
</script>
