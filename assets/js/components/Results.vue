<template>
  <div :class="classNames">
    <div v-for="(sectors, outcome) in data" :key="outcome">
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
    </div>
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
  data() {
    return {
      // Don't filter by FM, as that is handled via getValue
      filter_by: ["beneficiary", "sector", "area", "sdg_no", "thematic"],
    };
  },
  computed: {
    data() {
      if (!this.hasData) return [];

      const results = {};
      this.filtered.forEach((d) => {
        const sector = this.hideSector ? "" : d.sector;
        const header = d.header;
        const indicator = d.indicator.replace(/^Number of /, "");
        const value = this.getValue(d);

        if (value === 0) return;

        if (results[header] === undefined) {
          results[header] = {};
        }
        if (results[header][sector] === undefined) {
          results[header][sector] = {};
        }

        const currentValue = results[header][sector][indicator] || 0;
        results[header][sector][indicator] = currentValue + value;
      });

      return results;
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
    getValue(d) {
      switch (this.filters.fm) {
        case "EEA Grants":
          return parseFloat(d.achievement_eea);
        case "Norway Grants":
          return parseFloat(d.achievement_norway);
        default:
          return parseFloat(d.achievement_total);
      }
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

