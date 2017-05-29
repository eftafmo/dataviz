<template>
  <div class="sidebar-tab-pane results"
       v-bind:class="{
        'is-selected': selected,
        'is-loading': loading
       }">
    <ul class="sidebar-tab-result-list">
      <li v-for="item in data">
        <div class="sidebar-result-news">
          <div class="body">
            <h4 class="title">{{ item.outcome }}</h4>
            <small>{{ item.priority_sector_name }}</small>
            <ul v-for="ind in item.indicators" class="indicators">
               <li class="indicator clearfix" :style="{borderColor: color[item.priority_sector_id]}">
                  <div class="ind-count"> {{ ind.achievement }}</div>
                  <div class="ind-value"> {{ ind.indicator }} </div>
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
.results{
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

  .ind-count {
    display: inline;
    font-size: 2rem;
    color: black;
  }

  .country_thumbnail {
    display: inline-block;
    width: 24px;
    margin-right: .5rem;
  }

  .ind-country {
    display: flex;
    align-items: center;
    margin-bottom: .3rem;
  }

  .ind-value {
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
import WithCountriesMixin, {COUNTRIES, get_flag_name} from './mixins/WithCountries';

export default Vue.extend({
  mixins: [
    BaseMixin, WithCountriesMixin,
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

    methods: {
      loadResults() {
        var self = this;
        self.loading = true;

        window.setTimeout(function() {
          // simulate ajax call
          self.loading = false;
        }, 1000);
      },
    }

  });


</script>
