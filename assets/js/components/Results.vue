<template>
  <div class="sidebar-tab-pane"
       v-bind:class="{
        'is-selected': selected,
        'is-loading': loading
       }">
    <ul class="sidebar-tab-result-list" v-if="hasData">
      <li v-for="(item, outcome) in data">
        <div class="sidebar-result-news">
          <div class="body">
            <h4 class="title">{{ outcome }}</h4>
            <small>{{ item.sector }}</small>
            <ul v-for="(value, indicator) in item.indicators" class="indicators">
               <li class="indicator clearfix" :style="{borderColor: sectorcolour(item.sector)}">
                  <div class="indicator-achievement"> {{ value }}</div>
                  <div class="indicator-name"> {{ indicator }} </div>
               </li>
               </ul>
          </div>
        </div>
      </li>
    </ul>

    <div class="small muted align-center">
      &ndash;
      <button type="button" class="btn-link">show 10 more results</button>
      |
      <a href="#search" class="muted">show all</a>
      &ndash;
    </div>

  </div>
</template>

<style lang="less">
.sidebar-tab-pane {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
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

/*
  .country_thumbnail {
    display: inline-block;
    width: 24px;
    margin-right: .5rem;
  }

  .indicator-country {
    display: flex;
    align-items: center;
    margin-bottom: .3rem;
  }
*/

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
import {SectorColours} from 'js/constants.js';
//import WithCountriesMixin, {COUNTRIES, get_flag_name} from './mixins/WithCountries';
import WithSectorsMixin from './mixins/WithSectors';

export default Vue.extend({
  mixins: [
    BaseMixin, WithSectorsMixin,
  ],

  props: {
    selected: {
      type: Boolean,
      default: false
    },
  },

  watch: {
      selected () { this.loadResults(); }
  },

  data () {
    return {
      loading: false,
      color: SectorColours,
    }
  },

  computed: {
    data() {
      const dataset = this.filter(this.dataset);
      const results = {};

      for (const d of dataset) {
        for (const o in d.results) {
          const values = d.results[o];

          if (!values) continue;

          let outcome = results[o];
          if (outcome === undefined)
            outcome = results[o] = {
              sector: d.sector,
              indicators: {},
            };

          for (let i in values) {
            const value = +values[i];

            if (value === 0) continue;

            i = i.replace(/^Number of /, '');

            let sum = outcome.indicators[i] || 0;
            outcome.indicators[i] = sum + value;
          }
        }
      }

      // TODO: sorting order?

      return results;
    },
  },
  methods: {
    loadResults() {
      /*
      var self = this;
      self.loading = true;

      window.setTimeout(function() {
        // simulate ajax call
        self.loading = false;
      }, 1000);
      */
    },
  },
});

</script>
