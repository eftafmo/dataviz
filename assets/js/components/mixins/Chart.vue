<script>
import * as d3 from 'd3';
import Dropdown from '../includes/DropdownFilter.vue';

export default {
  components: {
    'dropdown': Dropdown,
  },

  data: function() {
    return {
      rendered: false,
      // settings this explicitly to null, so things fail with a bang
      // if initialized too early
      svgWidth: null,
      // default transition duration
      duration: 400,
    }
  },

  mounted() {
    this.chart = d3.select(this.$el).select('.chart');
    this.legend = d3.select(this.$el).select('.legend');
    window.addEventListener('resize', this.calculateSVGWidth);
    // don't forget to init
    this.calculateSVGWidth();
  },

  methods: {
    main() {
      // we need to do this during next tick, or render will get run
      // with zero svgWidth
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

    calculateSVGWidth(event) {
      const chart = this.chart.node(),
            elem = chart.ownerSVGElement ? chart.ownerSVGElement : chart;
      this.svgWidth = elem.getBoundingClientRect().width;
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
    window.removeEventListener('resize', this.calculateSVGWidth);
  },
};
</script>
