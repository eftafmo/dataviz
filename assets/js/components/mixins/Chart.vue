<script>
import * as d3 from 'd3';
import Dropdown from '../includes/DropdownFilter.vue';
import d3Tip from "d3-tip";
d3.tip = d3Tip;

export default {

  components: {
    'dropdown': Dropdown,
  },

  data: function() {
    return {
      // settings this explicitly to null, so things fail with a bang
      // if initialized too early
      svgWidth: null,
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
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.calculateChartWidth);
  },
};
</script>
