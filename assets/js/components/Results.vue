<template>
    <ul class="results" v-if="hasData">
      <li v-for="(items, outcome) in data">
        <div class="content-item results_content">
          <div class="body">
            <h4 class="title">{{ outcome }}</h4>
            <div v-for="(indicators, sector) in items">
              <small v-show="!filters.sector">{{ sector }}</small>
              <ul v-for="(value, indicator) in indicators" class="indicators">
                 <li class="indicator clearfix" :style="{borderColor: sectorcolour(sector)}">
                    <div class="indicator-achievement"> {{ value }}</div>
                    <div class="indicator-name"> {{ indicator }} </div>
                 </li>
              </ul>
            </div>
          </div>
        </div>
      </li>
    </ul>
</template>

<style lang="less">
.results {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
  }

  small {
    color: #898989;
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

import Vue from 'vue';
import * as d3 from 'd3';
import BaseMixin from './mixins/Base';
import WithSectorsMixin from './mixins/WithSectors';
import {FILTERS} from '../globals.js'

export default Vue.extend({
  mixins: [
    BaseMixin, WithSectorsMixin,
  ],

  computed: {
    data() {
      const dataset = this.filter(this.dataset);
      const results = {};

      for (const d of dataset) {
        const sector = d.sector;
        for (const o in d.results) {
          const values = d.results[o];

          if (!values) continue;

          let outcome = results[o];
          if (outcome === undefined)
            outcome = results[o] = {}
          if (outcome[sector] == undefined)
            outcome[sector] = {}

          for (let indicator in values) {
            const value = +values[indicator];

            if (value === 0) continue;

            indicator = indicator.replace(/^Number of /, '');

            let sum = outcome[indicator] || 0;
            outcome[sector][indicator] = sum + value;
          }
        }
      }

      // TODO: sorting order?
      return results;
    },
  },

});

</script>
