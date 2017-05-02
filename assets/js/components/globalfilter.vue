<template>
    <div class="global-filters">
    <transition name="bounce">
      <div v-if="checkFilter()" class="container">
        <div class="global-filters-inner">
            <div class="filters-label">
              Showing data for:
            </div>
            <ul class="list-filters">
             <transition-group name="list" tag="p">
                <li class="filter-item"
                     v-for="(item, type, value) in items"
                     :filter="type"
                     v-if="item != null"
                     @click="removeFilter()"
                     v-bind:key="item">
                  {{item}}
                  <span class="icon icon-close"></span>
                </li>
              </transition-group>
            </ul>
            <button @click="resetFilters()" class="no-btn muted" id="reset-filters">
              Reset filters <span class="icon icon-close"></span>
            </button>
        </div>
      </div>
    </transition>
    </div>
</template>


<style lang="less">

.filter-item {
  cursor: pointer;
  margin-left: .5rem;
}

.list-filters {
  overflow: hidden;
}

.global-filters {
  padding: 0;

  .container {
    padding: 0 3rem;
  }
}

.filter-item {
  display: inline-block;
}

.list-enter-active, .list-leave-active {
  transition: all 1s;
}
.list-enter, .list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.bounce-enter-active {
  animation: bounce-in .5s;
}
.bounce-leave-active {
  animation: bounce-out .5s;
}
@keyframes bounce-in {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.5);
  }
  100% {
    transform: scale(1);
  }
}
@keyframes bounce-out {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.5);
  }
  100% {
    transform: scale(0);
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
