<template>
    <div :remove="removeLastFilter()" class="global-filters" :class="{active: hasFilters}">
    <transition name="bounce">
      <div v-if="hasFilters" class="container">
        <div class="global-filters-inner">
            <div class="filters-label">
              Showing data for:
            </div>
            <ul class="list-filters">
             <transition-group name="list">
                <li class="filter-item"
                     v-for="(item, key) in data"
                     :filter="key"
                     v-if="item != null"
                     @click="removeFilter"
                     :key="key">
                 {{item.name}}: {{item.value}}
                </li>
              </transition-group>
            </ul>
            <button @click="resetFilters" class="no-btn muted" id="reset-filters">
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
  white-space: normal;
}

.global-filters {
  overflow: hidden;
  padding: 0;
  opacity: 0;
  visibility: hidden;
  transition: all 300ms;

  &.active {
    opacity: 1;
    visibility: visible;
  }

  .container {
    padding: .5rem 3rem;
  }
}

.filter-item {
  display: inline-block;
    &:after {
      content: "\E900";
      font-family: 'eeag-icons' !important;
      vertical-align: middle;
  }
 @media(max-width: 800px){
  display: block;
 }
}

.list-enter-active, .list-leave-active {
  transition: all .3s;
}
.list-enter, .list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.bounce-enter-active {
  animation: bounce-in .3s;
}
.bounce-leave-active {
  animation: bounce-out .3s;
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
import {FILTERS} from '../globals.js'
import {truncate} from 'js/lib/util';
import _programme_areas from 'js/constants/programme-areas.json5';
import {COUNTRIES} from './mixins/WithCountries';

export default Vue.extend({

  data: function () {
    return {
      items: FILTERS,
     }
   },

  beforeCreate() {
    this.format_pa = function(programme_area) {
      return _programme_areas[programme_area]['short_name'];
    };
    this.format_bs = function(country_code) {
      return COUNTRIES[country_code]['name'];
    }

    this.FILTER_SETTINGS = {
      fm: {name:'FM'},
      beneficiary: {name: 'BS', formatter: this.format_bs},
      sector: {name: 'PS', truncate: 20},
      area: {name:'PA', formatter: this.format_pa},
      donor: {name: 'DS'},
      DPP: {name: 'Programme partner', truncate: 60},
      dpp: {name: 'Project partner', truncate: 60},
    }
  },

  computed : {
    hasFilters() {
      let component_parent = document.getElementById('global-filters');
      for (const filter in FILTERS) {
        if (FILTERS[filter]) {
          component_parent.classList.add('visible') ;
          return true;
        }
      }
      component_parent.classList.remove('visible') ;
      return false;
    },
    data() {
      const filters = {}
      for (const key in FILTERS) {
        if (FILTERS[key]) {
          const settings = this.FILTER_SETTINGS[key];
          let filter_value = FILTERS[key];
          if (settings['formatter']) {
            filter_value = settings['formatter'](filter_value);
          }
          if (settings['truncate']) {
            filter_value = truncate(filter_value, settings['truncate']);
          }
          filters[key] = {
            name: settings['name'],
            value: filter_value,
          }
        }
      }
      return filters;
    },
  },


  methods: {
    removeFilter(e){
      const remove_el = e.target.getAttribute('filter')
      FILTERS[remove_el] = null;
    },

    removeLastFilter() {
      const $this=this;
      window.addEventListener("keyup", function(e){
        if (e.keyCode == 27) {
          if($this.$el.querySelector('.list-filters')){
          let last_filter = $this.$el.querySelector('.list-filters .filter-item:last-child').getAttribute('filter');
          FILTERS[last_filter] = null
          }
        }
      })
    },

    resetFilters(){
      for (const filter in FILTERS) {
        FILTERS[filter] = null
      }
    },
  },


});

</script>
