<template>
  <div id="global-filters" :class="{ on_top: hasFilters() }">
    <div
      v-if="hasFilters()"
      class="global-filters"
      :class="{ active: hasFilters() }"
    >
      <transition name="bounce">
        <div v-if="hasFilters" class="container">
          <div class="global-filters-inner">
            <div class="filters-label">Showing data for:</div>
            <transition-group name="list">
              <div
                v-for="(item, key) in Object.fromEntries(
                  Object.entries(data).filter((v) => v != null)
                )"
                :key="key"
                class="filter-item"
                @click="removeFilter(key)"
              >
                {{ item.name }}: {{ item.value }}
                <span class="icon icon-cross"></span>
              </div>
            </transition-group>
            <button id="reset-filters" class="no-btn" @click="resetFilters">
              Reset filters <span class="icon icon-cross"></span>
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { truncate } from "@js/lib/util";
import _programme_areas from "@js/constants/programme-areas.json5";
import { COUNTRIES } from "./mixins/WithCountries";

import WithFiltersMixin from "./mixins/WithFilters";

export default {
  mixins: [WithFiltersMixin],

  computed: {
    data() {
      const filters = {};
      for (const key in this.filters) {
        if (this.filters[key]) {
          const settings = this.FILTER_SETTINGS[key];
          let filter_value = this.filters[key];
          if (settings["formatter"]) {
            filter_value = settings["formatter"](filter_value);
          }
          if (settings["truncate"]) {
            filter_value = truncate(filter_value, settings["truncate"]);
          }
          filters[key] = {
            name: settings["name"],
            value: filter_value,
          };
        }
      }

      return filters;
    },
  },

  beforeCreate() {
    this.format_pa = function (programme_area) {
      return _programme_areas[programme_area]["short_name"];
    };
    this.get_country = function (country_code) {
      return COUNTRIES[country_code]["name"];
    };
    this.FILTER_SETTINGS = {
      fm: { name: "FM" },
      beneficiary: { name: "BS", formatter: this.get_country },
      region: { name: "Region" },
      sector: { name: "PS", truncate: 20 },
      sdg_no: { name: "SDG", formatter: (v) => v.toString() },
      area: { name: "PA", formatter: this.format_pa },
      donor: { name: "DS", formatter: this.get_country },
      DPP: { name: "Programme partner", truncate: 60 },
      dpp: { name: "Project partner", truncate: 60 },
      thematic: { name: "Criteria" },
    };
  },

  created() {
    this.filters_stack = [];

    this.initFiltersStack();
    this.handleEsc();
  },

  methods: {
    initFiltersStack() {
      for (const type in this.filters) {
        if (this.filters[type]) {
          this.filters_stack.push(type);
        }
      }
    },

    handleEsc() {
      const self = this;
      window.addEventListener("keyup", (e) => {
        if (e.keyCode == 27) self.removeLastFilter();
      });
    },

    hasFilters() {
      for (const filter in this.filters) {
        if (this.filters[filter]) {
          return true;
        }
      }
      return false;
    },

    removeFilter(key) {
      this.filters[key] = null;
    },

    // filters_stack holds the active filters ordered chronologically
    removeLastFilter() {
      if (this.filters_stack.length > 0) {
        const lastFilter = this.filters_stack[this.filters_stack.length - 1];
        this.filters[lastFilter] = null;
      }
    },

    resetFilters() {
      for (const filter in this.filters) {
        this.filters[filter] = null;
      }
    },

    // it is executed each time this.filters changes
    // it will keep track of all filters applied or removed, chronologically
    // if a previous same type filter is removed, then it will be removed from the list
    // but if it is changed after remove, the new one will be added as the most recent
    handleFilter(type, val, old) {
      const index = this.filters_stack.indexOf(type);
      if (index !== -1) this.filters_stack.splice(index, 1);
      if (val) this.filters_stack.push(type);
    },
  },
};
</script>

<style lang="less">
.on_top {
  z-index: 2;
}

.filter-item {
  cursor: pointer;
  margin-left: 0.5rem;
}

.list-filters {
  overflow: hidden;
  white-space: normal;
  @media (max-width: 800px) {
    margin-left: -2rem;
  }
}

#reset-filters {
  @media (max-width: 800px) {
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
    padding: 0.5rem 3rem;
    text-align: right;
  }
}

.global-filters .icon {
  font-size: 1rem;
}

.filters-label {
  @media (max-width: 800px) {
    display: none;
  }
}

.filter-item {
  display: inline-block;

  @media (max-width: 800px) {
    display: block;
  }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s;
}

.list-enter,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.bounce-enter-active {
  animation: bounce-in 0.3s;
}

.bounce-leave-active {
  animation: bounce-out 0.3s;
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