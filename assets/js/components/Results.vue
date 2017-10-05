<template>
    <ul :class="classNames">
     <div v-for="items in data">
      <li v-for="(sectors, outcome) in items">
        <div class="content-item results_content">
          <div class="body">
            <h4 class="title">{{ outcome }}</h4>
            <div v-for="(indicators, sector) in sectors">
              <small v-show="!filters.sector">{{ sector }}</small>
              <ul class="indicators">
                 <li v-for="(value, indicator) in indicators" class="indicator clearfix" :style="{borderColor: sectorcolour(sector)}">
                    <div class="indicator-achievement"> {{ value }}</div>
                    <div class="indicator-name"> {{ indicator }} </div>
                 </li>
              </ul>
            </div>
          </div>
        </div>
      </li>
     </div>
    </ul>
</template>


<style lang="less">
.dataviz .viz.results {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
  }

  small {
    color: #898989;
  }

  .title {
    color: #444;
  }

  .indicator {
    border-left: 3px solid red;
    margin-bottom: .5rem;
    padding-left: .5rem;
  }

  .indicator-achievement {
    display: inline;
    font-size: 2rem;
    color: black;
  }

  .indicator-name {
    display: inline;
    font-size: 1.2rem;

  }

}
</style>


<script>
import * as d3 from 'd3';

import Component from './Component';

import WithSectorsMixin from './mixins/WithSectors';


export default Component.extend({
  type: "results",

  mixins: [
    WithSectorsMixin,
  ],

  updated() {
  //TODO: this can be done a lot better
    if (window.matchMedia("(max-width: 800px)").matches) {
      const results_count = Object.keys(this.data[0]).length
      if (!results_count) return;
      const parent_nav = this.$el.parentNode.parentNode.parentNode.querySelector('[aria-controls="#results"]');
      if (!parent_nav) return;
      parent_nav.innerHTML = 'Results ('+results_count+')'
    }
  },

  computed: {
    data() {
      if (!this.hasData) return []

      const dataset = this.filtered;
      const results = {};

      for (const d of dataset) {
        const sector = d.sector;
        for (const o in d.results) {
          const values = d.results[o];

          if (!values) continue;

          for (let indicator in values) {
            const value = +values[indicator]['achievement'];
            if (value === 0) continue;

            const priority = values[indicator]['order'];
            if (results[priority] === undefined) {
              results[priority] = {}
            }
            if (results[priority][o] === undefined) {
              results[priority][o] = {}
            }
            if (results[priority][o][sector] === undefined) {
              results[priority][o][sector] = {}
            }
            let outcome = results[priority][o][sector];

            indicator = indicator.replace(/^Number of /, '');

            let sum = outcome[indicator] || 0;
            outcome[indicator] = sum + value;
          }
        }
      }

      // remove all SortOrder 3 indicators from results if higher priority indicators are available
      if (Object.keys(results).length > 1) {
        delete results['3'];
      }

      const flattened = [];
      // now flatten, hopefully ordered by priority *unguaranteed*
      for (const priority in results) {
        flattened.push(results[priority]);
      }
      // TODO: check sorting order when adding priority=1 indicators
      return flattened;
    },
  },

});
</script>
