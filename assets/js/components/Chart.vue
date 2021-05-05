<style lang="less">
/*
  // use this in conjunction with the `rendered` property. for example

  <div :class="{ rendering: !rendered }">
    ...
  </div>

  note that "rendering" is automatically added to `this.classNames`
*/
.dataviz .rendering {
  // (TODO: transition this?)
  visibility: hidden;
}
</style>

<script>
import * as d3 from 'd3';
import debounce from 'lodash.debounce';

import Component from './Component';
import ChartMixin from './mixins/Chart';

import Dropdown from './includes/DropdownFilter';


export default {
  extends: Component,

  mixins: [
    ChartMixin,
  ],

  components: {
    'dropdown': Dropdown,
  },

  data: function() {
    return {
      // these need to be synced with each component's css
      // TODO: load them from a common json / less-file?
      // default transition duration
      duration: 500,
      // alternate
      short_duration: 200,

      chart_rendered: false,
    };
  },

  computed: {
    rendered() {
      return this.chart_rendered;
    },
  },

  methods: {
    _getClassNames() {
      const names = this.$super(Chart, this)._getClassNames()
      if (!this.rendered) names.push("rendering")

      return names
    },

    main() {
      // we need to do the rendering during next tick only,
      // to allow ChartMixin.computeDimensions() to do its work
      this.$nextTick(this.render);
    },

    // this is automatically debounced by the ChartMixin
    render(initial) {
      // TODO: this smells like a bug-maker
      if (initial) this.chart_rendered = false;
      this.renderChart();
      this.chart_rendered = true;
    },

    renderChart() {
      throw new Error("Not implemented");
    },

    getTransition(duration) {
      // returns a transition that has 0 duration during first render
      if (!this.rendered) duration = 0
      else if (duration === undefined) duration = this.duration;

      return d3.transition()
               .duration(duration)
               .ease(d3.easeCubicOut)
    },

    // filters should re-render by default, unless specifically handled
    handleFilter() {
      this.render();
    },
  },
}
</script>
