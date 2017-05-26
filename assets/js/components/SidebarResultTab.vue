<template>
  <div class="sidebar-tab-pane"
       v-bind:class="{
        'is-selected': selected,
        'is-loading': loading
       }">
    <ul class="sidebar-tab-result-list">
      <li v-for="item in data.items">
        <a class="sidebar-result-news" target="_blank">
          <div class="body">
            <h4 class="title">{{ item.outcome }}</h4>
            <small>{{ item.priority_sector_name}}</small>
            <ul v-for="ind in item.indicators" class="indicators">
               <li v-for="(value,country) in ind.achievement" class="indicator clearfix" :style="{borderColor: color[item.priority_sector_name]}">
                  <div class="ind-country">
                    <img class="country_thumbnail" :src="`/assets/imgs/${get_flag_name(country)}.png`">
                    <small> {{get_country_name(country)}} </small>
                  </div>
                  <div class="ind-count"> {{value}}</div>
                  <div class="ind-value"> {{ind.indicator}} </div>
               </li>
               </ul>
          </div>
        </a>
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
.sidebar-tab-pane{
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
    float: left;
    font-size: 2rem;
    color: black;
    width: 10%;
  }

  .country_thumbnail {
    display: inline-block;
    width: 24px;
  }

  .ind-country {
    display: flex;
    align-items: center;
    margin-bottom: .3rem;
  }

  .ind-value {
    float: left;
    width: 90%;
  }

}
</style>

<script>

import Vue from 'vue';
import BaseMixin from './mixins/Base';
import {SectorColours} from 'js/constants.js';
import WithCountriesMixin, {COUNTRIES, get_flag_name} from './mixins/WithCountries';
import mydata from 'js/dummy.js';
console.log(mydata)

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
        dataset: {
         items: mydata,
        }
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
