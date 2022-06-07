<template>
  <div v-if="hasData && gridItems.length > 0" class="overview-results">
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
      filter_by: ["beneficiary"],
    };
  },
  computed: {
    filtered() {
      return this.filter(this.dataset, this.filter_by);
    },

    aggregated() {
      return this.aggregate(
        this.filtered,
        ["indicator"],
        ["achievement_eea", "achievement_norway", "achievement_total"],
        false
      );
    },
    gridItems() {
      return [
        // 2014-2021
        {
          id: "civil-soa",
          image: "imgs/results/icon_people.svg",
          amount: this.getAmount(
            "Number of people engaged in civil society organisation activities (including online)"
          ),
          description:
            "people involved in civil society organisation activities",
        },
        {
          id: "co2-reduction",
          image: "imgs/results/icon_emissions.svg",
          amount: this.getAmount("Estimated annual CO2 emissions reductions"),
          description: "tons of est. annual CO2 emissions reduction",
        },
        this.getAmount("Number of researchers supported") > 0
          ? {
              id: "researchers",
              image: "imgs/results/icon_researchers.svg",
              amount: this.getAmount("Number of researchers supported"),
              description: "supported researchers",
            }
          : {
              id: "staff-trained",
              image: "imgs/results/icon_researchers.svg",
              amount: this.getAmount("Number of professional staff trained"),
              description: "professional staff trained",
            },
        {
          id: "jobs",
          image: "imgs/results/icon_jobs.svg",
          amount: this.getAmount("Number of jobs created"),
          description: "jobs created",
        },
        // 2009-2014
        {
          id: "anual-co2-reduction",
          image: "imgs/results/icon_emissions.svg",
          amount: this.getAmount(
            "Estimated CO2 reduction and/or avoidance in tonnes/year"
          ),
          description: "tons of est. annual CO2 emissions reduced",
        },
        {
          id: "green-jobs",
          image: "imgs/results/icon_jobs.svg",
          amount: this.getAmount("Number of green jobs created"),
          description: "green jobs created",
        },
        {
          id: "ngos-supported",
          image: "imgs/results/icon_researchers.svg",
          amount: this.getAmount(
            "Number of NGOs/small organisations reporting strengthened capacity"
          ),
          description: "ngos and small organisations supported",
        },
        {
          id: "basic-welfare",
          image: "imgs/results/icon_people.svg",
          amount: this.getAmount(
            "Number of beneficiaries reporting improved access to basic and welfare services"
          ),
          description:
            "people with improved access to basic and welfare services",
        },
      ].filter((item) => item.amount > 0);
    },
  },
  methods: {
    getAmount(key) {
      const values = this.aggregated[key];
      if (!values) return 0;

      switch (this.filters.fm) {
        case "EEA Grants":
          return values.achievement_eea;
        case "Norway Grants":
          return values.achievement_norway;
        default:
          return values.achievement_total;
      }
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
