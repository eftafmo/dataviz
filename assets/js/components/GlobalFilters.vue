<template>
  <div class="global-filters" :class="{active: hasFilters()}">
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
                   :data-filter="key"
                   v-if="item != null"
                   @click="removeFilter"
                   :key="key">
               {{item.name}}: {{item.value}}
              </li>
            </transition-group>
          </ul>
          <button @click="resetFilters" class="no-btn" id="reset-filters">
            Reset filters <span class="icon icon-cross"></span>
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
  @media(max-width: 800px){
    margin-left: -2rem;
  }
}

#reset-filters {
  @media(max-width: 800px) {
    margin-right: -2rem;
  }
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
.global-filters .icon {
  font-size: 1rem;
}

.filters-label {
  @media(max-width:800px){
    display: none;
  }
}

.filter-item {
  display: inline-block;
 @media(max-width: 800px){
  display: block;
  &:after {
    position: absolute;
  }
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
import {truncate} from 'js/lib/util';
import _programme_areas from 'js/constants/programme-areas.json5';
import {COUNTRIES} from './mixins/WithCountries';

import WithFiltersMixin from './mixins/WithFilters'


export default Vue.extend({
  mixins: [
    WithFiltersMixin,
  ],

  beforeCreate() {
    const $this = this
    this.format_pa = function(programme_area) {
      return _programme_areas[programme_area]['short_name'];
    };
    this.get_country = function(country_code) {
      return COUNTRIES[country_code]['name'];
    }
    this.FILTER_SETTINGS = {
      fm: {name:'FM'},
      beneficiary: {name: 'BS', formatter: this.get_country},
      sector: {name: 'PS', truncate: 20},
      area: {name:'PA', formatter: this.format_pa},
      donor: {name: 'DS', formatter: this.get_country},
      DPP: {name: 'Programme partner', truncate: 60},
      dpp: {name: 'Project partner', truncate: 60},
    }
  },

  computed: {
    data() {
      const filters = {}
      for (const key in this.filters) {
        if (this.filters[key]) {
          const settings = this.FILTER_SETTINGS[key];
          let filter_value = this.filters[key];
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

  created() {
    const self = this;
    this.chronologicalFilters = [];

    this.makeChronologicalFiltersFromExisting();
    this.handleEsc();
  },

  methods: {
    makeChronologicalFiltersFromExisting() {
      for(var i in this.filters) {
        if(this.filters[i]) {
          this.chronologicalFilters.push({type: i, val: this.filters[i]});
        }
      }
    },

    handleEsc() {
      let self = this;
      window.addEventListener("keyup", function(e) {
        if (e.keyCode == 27) {
          self.removeLastFilter();
        }
      });
    },

    hasFilters() {
      let component_parent = document.getElementById('global-filters');
      for (const filter in this.filters) {
        if (this.filters[filter]) {
          component_parent.classList.add('visible') ;
          return true;
        }
      }
      component_parent.classList.remove('visible') ;
      return false;
    },

    removeFilter(e) {
      const remove_el = e.target.dataset.filter;
      this.filters[remove_el] = null;
    },
    // chronologicalFilters holds the active filters ordered chronologically
    removeLastFilter() {
      let removedFilter = this.chronologicalFilters[this.chronologicalFilters.length-1];
      this.filters[removedFilter.type] = null;
    },
    
    resetFilters() {
      for (const filter in this.filters) {
        this.filters[filter] = null
      }
      this.chronologicalFilters = [];
    },
    // it is executed each time this.filters changes
    // it will keep track of all filters applied or removed, chronologically
    // if a previous same type filter is removed, then it will be removed from the list
    // but if it is changed after remove, the new one will be added as the most recent
    handleFilter(type, val, old) {
      if(old) {
        this.removeOneFilter(type, val);
        if(val) {
          this.chronologicalFilters.push({type, val});
        }
      } else {
        if(val) {
          this.chronologicalFilters.push({type, val});
        }
      }
    },

    removeOneFilter(type, val) {
      for(var i=0; i<this.chronologicalFilters.length; i++) {
        if(this.chronologicalFilters[i].type === type) {
          this.chronologicalFilters.splice(i, 1);
        }
      }
    }
  },
});

</script>