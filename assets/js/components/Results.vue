<template>
  <div :class="classNames">
    <ul class="indicators">
      <li
        v-for="(value, indicator) in data"
        :key="indicator"
        class="indicator clearfix"
      >
        <div class="indicator-achievement">{{ number(value) }}</div>
        <div class="indicator-name">{{ indicator }}</div>
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
        const value = this.getValue(d);
        const indicator = d.indicator.replace(/^Number of /, "");

        if (value === 0) return;

        results[indicator] = (results[indicator] || 0) + value;
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
    border-left: 3px solid #3b5998;
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

