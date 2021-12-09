<template>
  <div :class="classNames">
    <ul v-for="(items, index) in data" :key="index">
      <li v-for="(sectors, outcome) in items" :key="outcome">
        <div class="content-item results_content">
          <div class="body">
            <h4 class="title">{{ outcome }}</h4>
            <div v-for="(indicators, sector) in sectors" :key="sector">
              <small v-show="!filters.sector && !hideSector">
                {{ sector }}
              </small>
              <ul class="indicators">
                <li
                  v-for="(value, indicator) in indicators"
                  :key="indicator"
                  class="indicator clearfix"
                  :style="{ borderColor: getColor(sector) }"
                >
                  <div class="indicator-achievement">{{ number(value) }}</div>
                  <div class="indicator-name">{{ indicator }}</div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import Component from "./Component";

import WithSectorsMixin from "./mixins/WithSectors";

export default {
  extends: Component,
  type: "results",
  mixins: [WithSectorsMixin],
  props: {
    hideSector: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    data() {
      if (!this.hasData) return [];

      const dataset = this.filtered;
      const results = {};

      for (const d of dataset) {
        let sector = "";

        if (!this.hideSector) {
          sector = d.sector;
        }

        for (const o in d.results) {
          const values = d.results[o];

          if (!values) continue;

          for (let indicator in values) {
            const priority = values[indicator]["order"];
            // If there is a FM set the data is already filtered so, the value is
            // achievement is already the total and correct one that needs to be displayed.
            // Otherwise, use the `achievement_total` from the backend as that
            // will include results that cannot be allocated to either EEA or Norway
            const value = this.filters.fm
              ? +values[indicator]["achievement"]
              : +values[indicator]["achievement_total"];

            if (value === 0) continue;

            if (results[priority] === undefined) {
              results[priority] = {};
            }
            if (results[priority][o] === undefined) {
              results[priority][o] = {};
            }
            if (results[priority][o][sector] === undefined) {
              results[priority][o][sector] = {};
            }
            const outcome = results[priority][o][sector];
            indicator = indicator.replace(/^Number of /, "");
            outcome[indicator] = value;
          }
        }
      }

      // remove all SortOrder 3 indicators from results if higher priority indicators are available
      if (Object.keys(results).length > 1) {
        delete results["3"];
      }

      const flattened = [];
      // now flatten, hopefully ordered by priority *unguaranteed*
      for (const priority in results) {
        flattened.push(results[priority]);
      }
      // TODO: check sorting order when adding priority=1 indicators
      return flattened;
    },
  },
  updated() {
    //TODO: this can be done a lot better
    if (window.matchMedia("(max-width: 800px)").matches) {
      const results_count = Object.keys(this.data[0]).length;
      if (!results_count) return;
      const parent_nav =
        this.$el.parentNode.parentNode.parentNode.querySelector(
          '[aria-controls="#results"]'
        );
      if (!parent_nav) return;
      parent_nav.innerHTML = "Results (" + results_count + ")";
    }
  },
  methods: {
    getColor(sector) {
      if (!sector) return "#3b5998";
      return this.sectorcolor(sector);
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.results {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
  }

  small {
    color: #898989;
  }

  .title {
    color: #444;
  }

  .indicator {
    border-left: 3px solid red;
    margin-bottom: 0.5rem;
    padding-left: 0.5rem;
  }

  .indicator-achievement {
    display: inline;
    font-size: 2rem;
    color: black;
    margin-right: 0.2rem;
  }

  .indicator-name {
    display: inline;
    font-size: 1.2rem;
  }
}
</style>

