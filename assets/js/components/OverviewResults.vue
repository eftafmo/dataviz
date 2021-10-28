<template>
  <div
    v-if="hasData && aggregated.allocation && gridItems.length > 0"
    class="overview-results"
  >
    <embeddor :period="period" tag="overview_results" />
    <div class="overview-heading extra-bold">
      <span class="muted">The</span>
      <dropdown-filter
        filter="fm"
        title="EEA and Norway Grants"
        :items="FM_ARRAY"
        class="viz-select-heading"
      />
      <span class="muted">results in</span>
      <dropdown-filter
        filter="beneficiary"
        title="all Beneficiary States"
        :items="BENEFICIARY_ARRAY"
        class="viz-select-heading"
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
        <img :src="getAssetUrl(item.image)" alt="" />
        <div class="amount extra-bold">{{ shortNumber(item.amount) }}</div>
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
        [
          "allocation",
          // 2014-2021
          "people_civil_society",
          "jobs_created",
          "supported_researchers",
          "staff_trained",
          "co2_emissions_reduction",
          // 2009-2014
          "annual_co2_emissions_reduced",
          "green_jobs_created",
          "ngos_small_organisations_supported",
          "people_improved_access",
        ],
        false
      );
    },
    gridItems() {
      return [
        // 2014-2021
        {
          id: "civil-soa",
          image: "imgs/results/icon_people.svg",
          amount: this.aggregated.people_civil_society,
          description:
            "people involved in civil society organisation activities",
        },
        {
          id: "co2-reduction",
          image: "imgs/results/icon_emissions.svg",
          amount: this.aggregated.co2_emissions_reduction,
          description: "tons of est. annual CO2 emissions reduction",
        },
        this.aggregated.supported_researchers > 0
          ? {
              id: "researchers",
              image: "imgs/results/icon_researchers.svg",
              amount: this.aggregated.supported_researchers,
              description: "supported researchers",
            }
          : {
              id: "staff-trained",
              image: "imgs/results/icon_researchers.svg",
              amount: this.aggregated.staff_trained,
              description: "professional staff trained",
            },
        {
          id: "jobs",
          image: "imgs/results/icon_jobs.svg",
          amount: this.aggregated.jobs_created,
          description: "jobs created",
        },
        // 2009-2014
        {
          id: "anual-co2-reduction",
          image: "imgs/results/icon_emissions.svg",
          amount: this.aggregated.annual_co2_emissions_reduced,
          description: "tons of est. annual CO2 emissions reduced",
        },
        {
          id: "green-jobs",
          image: "imgs/results/icon_jobs.svg",
          amount: this.aggregated.green_jobs_created,
          description: "green jobs created",
        },
        {
          id: "ngos-supported",
          image: "imgs/results/icon_researchers.svg",
          amount: this.aggregated.ngos_small_organisations_supported,
          description: "ngos and small organisations supported",
        },
        {
          id: "basic-welfare",
          image: "imgs/results/icon_people.svg",
          amount: this.aggregated.people_improved_access,
          description:
            "people with improved access to basic and welfare services",
        },
      ].filter((item) => item.amount > 0);
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
  margin-bottom: 7rem;
  .muted {
    color: #f7c5c4;
  }

  .viz-select-heading {
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

    img {
      max-width: 5rem;
      max-height: 5rem;
    }

    .amount {
      color: #ffffff;
      font-size: 6rem;
      margin-left: 3rem;
      font-weight: bold;
      min-width: 15rem;
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
