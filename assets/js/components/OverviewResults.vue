<template>
  <div v-if="hasData && aggregated.allocation" class="overview-results">
    <embeddor tag="overview_results" />
    <div class="overview-heading">
      <span class="muted">The</span>
      <dropdown-filter
        filter="fm"
        title="EEA and Norway Grants"
        :items="FM_ARRAY"
        class="viz-select-overview"
      />
      <span class="muted">results in</span>
      <dropdown-filter
        filter="beneficiary"
        title="all Beneficiary States"
        :items="BENEFICIARY_ARRAY"
        class="viz-select-overview"
      />
      <span class="muted">at a glance</span>
    </div>
    <div class="overview-results-grid">
      <div
        v-for="item in gridItems"
        :key="item.id"
        class="grid-item"
        :class="{ hidden: !!item.hidden }"
      >
        <img :src="`/assets/sprites/${item.image}`" alt="" />
        <div class="amount">{{ item.amount }}</div>
        <div class="description">{{ item.description }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import Component from "./Component";
import WithFMsMixin from "./mixins/WithFMs";
import WithCountriesMixin from "./mixins/WithCountries";
import DropdownFilter from "./includes/DropdownFilter";
import Embeddor from "./includes/Embeddor";

export default {
  components: { Embeddor, DropdownFilter },
  extends: Component,
  type: "overview",
  mixins: [WithFMsMixin, WithCountriesMixin],
  data() {
    return {
      filter_by: ["fm", "beneficiary"],
    };
  },
  computed: {
    aggregated() {
      return this.aggregate(
        this.filtered,
        [],
        ["allocation", "project_count", { source: "programmes", type: Array }],
        false
      );
    },
    gridItems() {
      return [
        {
          id: "civil-soa",
          image: "placeholder.png",
          amount: "N/A",
          description:
            "people involved in civil society organisation activities",
        },
        {
          id: "co2-reduction",
          image: "placeholder.png",
          amount: "N/A",
          description: "tons of est. annual CO2 emissions reduction",
        },
        {
          id: "researchers",
          image: "placeholder.png",
          amount: "N/A",
          description: "supported researchers",
        },
        {
          id: "jobs",
          image: "placeholder.png",
          amount: "N/A",
          description: "jobs created",
        },
      ];
    },
  },
};
</script>

<style lang="less" scoped>
.overview-results {
  background-color: #dc4844;
  margin-top: -1px;
  padding: 6rem 0;
}

.dataviz .overview-heading {
  .muted {
    color: #f7c5c4;
  }

  .viz-select-overview::v-deep {
    color: #ffffff;
  }
}

.overview-results-grid {
  display: grid;
  grid-row-gap: 7.5rem;
  grid-column-gap: 2rem;
  grid-template-columns: 1fr 1fr;

  max-width: 120rem;
  margin: auto;
  padding: 0 2rem;

  .grid-item {
    display: flex;
    align-items: center;

    &.hidden {
      display: none;
    }

    .amount {
      color: #ffffff;
      font-size: 3.6rem;
      margin-left: 3rem;
      font-weight: bold;
    }

    .description {
      color: #222222;
      font-size: 2.4rem;
      line-height: 1;
      font-weight: bold;
      text-transform: uppercase;
      margin-left: 1.6rem;
      max-width: 28.6rem;
    }
  }
}

@media (max-width: 800px) {
  .overview-results {
    padding: 2rem 0;
  }

  .overview-results-grid {
    .grid-item {
      flex-wrap: wrap;

      .amount {
        flex-grow: 1;
      }

      .description {
        flex-grow: 1;
        flex-basis: 100%;
        margin-left: 0;
        margin-top: 1rem;
      }
    }
  }
}

@media (max-width: 600px) {
  .overview-results-grid {
    grid-template-columns: 1fr;
    grid-row-gap: 4rem;

    .grid-item {
      align-items: center;
    }
  }
}
</style>
