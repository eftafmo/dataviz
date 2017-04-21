<script>
import * as d3 from 'd3';

export default {
  mounted() {
    this.chart = d3.select(this.$el).select('.chart');
    this.legend = d3.select(this.$el).select('.legend');
  },

  methods: {
    main() {
      this.render();
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
  },
};
</script>
