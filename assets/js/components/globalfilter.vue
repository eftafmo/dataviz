<template>
    <div class="global-filter">
        <span class="filter-item"
         v-for="(item, type) in items"
         :filter="type"
         @click="removeFilter()">
        {{item}}
        </span>
    </div>
</template>


<style lang="less">

.global-filter {
  background: #50B9FF;
  color: white;
}
.filter-item {
  // padding: .5rem;
  margin-right: 1rem;
  margin-left: .5rem;
  // display: inline;
}

</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';
import {FILTERS} from './global/filters.js'



export default Vue.extend({
  props : {
    item: String,
    filter: String,
  },

  data: function () {
    return {
      items: FILTERS,
     }
   },


  methods: {
    removeFilter(){
      var remove_el = event.target.getAttribute('filter')
      FILTERS[remove_el] = null;
    }
  },


});

</script>
