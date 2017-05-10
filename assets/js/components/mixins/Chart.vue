<script>
import * as d3 from 'd3';
import Dropdown from '../includes/DropdownFilter.vue';

export default {

  components: {
    'dropdown': Dropdown,
  },

  data: function() {
    return {
      width: 0,
    }
  },

  mounted() {
    this.chart = d3.select(this.$el).select('.chart');
    this.legend = d3.select(this.$el).select('.legend');
    window.addEventListener('resize', this.calculateChartWidth);
    // remember to init
    this.calculateChartWidth();
  },

  methods: {
    main() {
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
    calculateChartWidth(event) {
      const _chart = this.chart.node(),
            elem = _chart.ownerSVGElement ? _chart.ownerSVGElement : _chart;
      this.width = elem.getBoundingClientRect().width;
      // console.log(this.width);
    },
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.calculateChartWidth);
  },
};
</script>
