<template>
    <div class="global-filters">
      <div v-if="checkFilter()" class="container">
        <div class="global-filters-inner">
          <div class="filters-label">
            Showing data for:
          </div>
            <ul class="list-filters">
              <li class="filter-item"
               v-for="(item, type, value) in items"
               :filter="type"
               v-if="item != null"
               @click="removeFilter()">
                {{item}}
                <span class="icon icon-close"></span>
              </li>
            </ul>
            <button @click="resetFilters()" class="no-btn muted" id="reset-filters">
              Reset filters <span class="icon icon-close"></span>
            </button>
        </div>
      </div>
    </div>
</template>


<style lang="less">

.filter-item {
  cursor: pointer;
  margin-left: .5rem;
}

.global-filters {
  padding: 0;

  .container {
    padding: .5em 3rem;
  }
}

</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';
import {FILTERS} from './global/filters.js'

export default Vue.extend({

  data: function () {
    return {
      items: FILTERS,
     }
   },

  methods: {
    removeFilter(){
      var remove_el = event.target.getAttribute('filter')
      FILTERS[remove_el] = null;
    },

    resetFilters(){
      Object.keys(FILTERS).forEach(function(key) {
         FILTERS[key]=null
      });
    },

    checkFilter(){
      var return_val;
      Object.keys(FILTERS).forEach(function(key) {
          if(FILTERS[key]!=null){
            console.log(FILTERS[key]);
            return_val = true;
          }
      });
      return return_val
    }
  },


});

</script>
