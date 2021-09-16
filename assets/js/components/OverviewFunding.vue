<template>
  <div v-if="hasData && aggregated.allocation" class="overview-funding">
    <embeddor :period="period" tag="overview_funding" />
    <div class="overview-heading">
      <span class="muted">The</span>
      <dropdown-filter
        filter="fm"
        title="EEA and Norway Grants"
        :items="FM_ARRAY"
        class="viz-select-heading"
      />
      <span class="muted">funding for</span>
      <dropdown-filter
        filter="beneficiary"
        title="all Beneficiary States"
        :items="BENEFICIARY_ARRAY"
        class="viz-select-heading"
      />
      <span class="muted">at a glance</span>
    </div>
    <div class="overview-grid">
      <template v-for="category in gridItems" :key="category.id">
        <div class="row-header">
          <a :href="category.link" class="name">
            <span>{{ category.name }}</span>
            <span>&nbsp;&rightarrow;</span>
          </a>
          <div class="description">{{ category.description }}</div>
        </div>
        <div
          v-for="item in category.items"
          :key="item.id"
          class="row-item"
          :class="{ hidden: !!item.hidden }"
        >
          <div class="amount">{{ item.amount }}</div>
          <div class="name">{{ item.name }}</div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import Component from "./Component";
import WithFMsMixin from "./mixins/WithFMs";
import WithCountriesMixin from "./mixins/WithCountries";
import DropdownFilter from "./includes/DropdownFilter";
import Embeddor from "./includes/Embeddor";
import { sum } from "../lib/util";

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
      // XXX DPP = Donor Programme Partners
      // XXX dpp = donor project partners
      // XXX Yes, I know, it's dumb!
      return this.aggregate(
        this.filtered,
        [],
        [
          "allocation",
          "bilateral_fund",
          { source: "programmes", type: Array },
          { source: "projects", type: Array },
          { source: "positive_fx", type: Array },
          { source: "DPP_programmes", type: Array },
          { source: "dpp_projects", type: Array },
          { source: "bilateral_initiatives", type: Array },
          { source: "continued_coop", type: Array },
          { source: "beneficiary", type: String },
        ],
        false
      );
    },
    allocationByFm() {
      return this.FM_ARRAY.map((fm) => {
        const allocation = sum(
          this.filtered
            .filter((item) => item.fm === fm.name)
            .map((item) => parseFloat(item.allocation))
        );
        return {
          id: fm.id,
          name: fm.name,
          allocation,
          amount: this.shortCurrency(allocation),
          // Hide funding methods with no allocation in the currently filtered data.
          hidden: allocation <= 0,
        };
      });
    },
    programmesCount() {
      return Array.from(this.aggregated.programmes).filter((programme) => {
        const [country, code] = programme.split("-");

        // Programme Area PA05 is excluded while not filtering by a country
        // because SDDW already includes them.
        if (
          !this.filters.beneficiary &&
          code === "DECENTWORK" &&
          country !== "XX"
        )
          return false;

        return true;
      }).length;
    },
    gridItems() {
      return [
        {
          id: "funding",
          name: "Funding",
          link: `/${this.period}/funding/`,
          description:
            "Donec bibendum eros a velit ullamcorper ullamcorper. Sed eu temporquam. " +
            "Praesent imperdiet felis vitae pretium eleifend.",
          items: [
            ...this.allocationByFm,
            {
              id: "programmes",
              amount: this.number(this.programmesCount),
              name: "Programmes",
            },
            {
              id: "bilateral-fund",
              amount: this.shortCurrency(this.aggregated.bilateral_fund),
              name: "Bilateral fund",
            },
          ],
        },
        {
          id: "cooperation",
          name: "Cooperation",
          link: `/${this.period}/cooperation/`,
          description:
            "Quisque volutpat diam orci, ut dignissim elit cursus sit amet. " +
            "Donec euismod quam eget ipsum accumsan congue. Nulla tempus elit sed maximus elementum. " +
            "Duis ac ipsum dui. Suspendisse posuere neque eget finibus dignissim. " +
            "Mauris quis quam libero",
          items: [
            {
              id: "prg-part",
              name: "Programmes with a Donor partner",
              amount: this.number(this.aggregated.DPP_programmes.size),
            },
            {
              id: "prj-part",
              name: "Projects with a Donor partner",
              amount: this.number(this.aggregated.dpp_projects.size),
            },
            {
              id: "bil-init",
              name: "Bilateral initiatives",
              amount: this.number(this.aggregated.bilateral_initiatives.size),
            },
            {
              id: "part-cont",
              name: "Partnerships likely to continue",
              amount: this.number(this.aggregated.continued_coop.size),
            },
          ],
        },
        {
          id: "projects",
          name: "Projects",
          link: `/${this.period}/projects/`,
          description:
            "Vestibulum purus turpis, ultrices sed metus bibendum, faucibus tempor tortor. " +
            "Vivamus auctor est dui, eget sodales tellus tempus in. " +
            "Nulla vel posuere erat, in mattis sem.",
          items: [
            {
              id: "proj",
              name: "Projects",
              amount: this.number(this.aggregated.projects.size),
            },
            {
              id: "bs",
              name: "Beneficiary States",
              amount: this.number(this.aggregated.beneficiary.size),
              hidden: this.aggregated.beneficiary.size <= 1,
            },
            {
              id: "proj-pos",
              name: "Projects with lasting effect",
              amount: this.number(this.aggregated.positive_fx.size),
            },
          ],
        },
      ];
    },
  },
};
</script>

<style lang="less" scoped>
.overview-funding {
  margin-top: 4rem;
  background-color: #f5f5f5;
  padding: 6rem 0;
}

.overview-grid {
  display: grid;
  grid-row-gap: 10rem;
  grid-column-gap: 2rem;
  grid-template-columns: repeat(5, 1fr);

  max-width: 160rem;
  margin: auto;
  padding: 0 2rem;

  .row-header {
    grid-column-start: 1;
    grid-column-end: 1;
    max-width: 30rem;

    .name {
      color: #3b5998;
      font-size: 2.5rem;
      font-weight: bold;
      margin-bottom: 0.4rem;
      text-transform: uppercase;
    }

    .description {
      font-size: 1.5rem;
      color: #333333;
    }
  }

  .row-item {
    max-width: 23rem;
    line-height: 1;

    &.hidden {
      display: none;
    }

    .amount {
      color: #dc4844;
      font-size: 6rem;
      font-weight: bold;
      line-height: 1;
      margin-bottom: 0.4rem;
    }
    .name {
      color: #333333;
      font-size: 2.4rem;
      font-weight: bold;
      text-transform: uppercase;
    }
  }
}

@media (max-width: 980px) {
  .overview-funding {
    padding: 2rem 0;
  }

  .overview-grid {
    grid-template-columns: 1fr 1fr 1fr;
    grid-row-gap: 2rem;
    grid-column-gap: 2rem;

    .row-header {
      grid-column-start: 1;
      grid-column-end: 4;
      max-width: unset;
      border-top: 1px solid #cccccc;
      padding-top: 2rem;
    }

    .row-header:first-of-type {
      border: none;
      padding: 0;
    }
  }
}

@media (max-width: 768px) {
  .overview-grid {
    grid-template-columns: 1fr 1fr;
    grid-row-gap: 2rem;
    grid-column-gap: 2rem;

    .row-header {
      grid-column-start: 1;
      grid-column-end: 3;
    }
  }
}

@media (max-width: 600px) {
  .overview-grid {
    grid-template-columns: 1fr;

    .row-header {
      grid-column-start: 1;
      grid-column-end: 2;
    }

    .row-item {
      max-width: unset;
    }
  }
}
</style>
