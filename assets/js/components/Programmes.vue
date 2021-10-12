<template>
  <ul :class="classNames">
    <li v-for="beneficiary in data.beneficiaries" :key="beneficiary.id">
      <div class="content-item programmes_content">
        <div class="body">
          <div class="title-wrapper" @click="toggleContent($event)">
            <div class="flag">
              <img :src="`${get_flag(beneficiary.id)}`" alt="" />
            </div>
            <h3 class="title">{{ get_country_name(beneficiary.id) }}</h3>
            <small>({{ beneficiary.programmes.length }} programmes)</small>
          </div>
          <ul class="programme-list" :class="[{ active: filters.beneficiary }]">
            <li
              v-for="programme in beneficiary.programmes"
              :key="programme.programme_code"
              class="programme-item"
            >
              <slot
                name="programme-content"
                :programme="programme"
                :beneficiary="beneficiary"
              >
                <a
                  class="programme-sublist-item"
                  target="_blank"
                  :href="programme.programme_url"
                >
                  {{ programme.programme_name }}
                </a>
              </slot>
            </li>
          </ul>
        </div>
      </div>
    </li>
  </ul>
</template>

<script>
import * as d3 from "d3";

import Component from "./Component";
import WithCountriesMixin from "./mixins/WithCountries";
import WithRegionsMixin from "./mixins/WithRegions";

export default {
  extends: Component,
  type: "programmes",

  mixins: [WithCountriesMixin, WithRegionsMixin],

  computed: {
    data() {
      if (!this.hasData) return [];

      const dataset = this.filtered;
      const beneficiaries = {};
      let programmes_array = [];

      for (const d of dataset) {
        const programmes = d.programmes;

        if (!programmes || !Object.keys(programmes).length) continue;

        let beneficiary = beneficiaries[d.beneficiary];
        if (beneficiary === undefined)
          beneficiary = beneficiaries[d.beneficiary] = {};

        for (const p in programmes) {
          let programme = beneficiary[p];
          if (programme === undefined)
            programme = beneficiary[p] = {
              sector: d.sector,
              // TODO: programmes may have multiple sectors, see CZ02
              programme_code: p,
              programme_name: programmes[p].name,
              programme_url: programmes[p].url,
              nuts: programmes[p].nuts ? Object.keys(programmes[p].nuts) : null,
            };
          else if (programme.nuts) {
            // need to merge their nuts
            programme.nuts = Array.from(
              new Set(programme.nuts.concat(Object.keys(programmes[p].nuts)))
            );
          }
        }
      }

      const out = {
        beneficiaries: [],
        projectcount: 0,
      };

      for (const b in beneficiaries) {
        const programmes = beneficiaries[b],
          beneficiary = {
            id: b,
            ...this.allCountries[b],
            programmes: [],
          };
        out.beneficiaries.push(beneficiary);

        for (const p in programmes) {
          if (programmes[p].programme_code) out.projectcount += 1;
          const programme = programmes[p];
          if (this.isRelevantForSelectedRegion(programme)) {
            beneficiary.programmes.push(programme);
          }
        }
        // Sort by programme code, the Tripartite programme always last
        beneficiary.programmes.sort((a, b) =>
          d3.ascending(
            a.programme_code.replace("IN22", "ZZZZ"),
            b.programme_code.replace("IN22", "ZZZZ")
          )
        );
      }

      //Sort by country sortOrder
      out.beneficiaries.sort((a, b) => a.sortOrder - b.sortOrder);

      return out;
    },
  },

  updated() {
    //TODO: this can be done a lot better
    if (window.matchMedia("(max-width: 800px)").matches) {
      const parent_nav =
        this.$el.parentNode.parentNode.parentNode.querySelector(
          '[aria-controls="#programmes"]'
        );
      if (!parent_nav) return;
      parent_nav.innerHTML = "Programmes (" + this.data.projectcount + ")";
    }
  },

  methods: {
    toggleContent(e) {
      //remove comment if you want to toggle between elements

      // let all_programe_items = this.$el.querySelectorAll('.programme-item');
      // for (let item of all_programe_items){
      //     if(item.classList.contains('active'))
      //         item.classList.remove('active')
      // }

      //TODO : get rid of the parenNode logic
      let target;
      if (e.target.parentNode.classList.contains("flag"))
        target =
          e.target.parentNode.parentNode.parentNode.querySelector(
            ".programme-list"
          );
      else
        target =
          e.target.parentNode.parentNode.querySelector(".programme-list");
      if (target.classList.contains("active")) {
        target.classList.remove("active");
      } else {
        target.classList.add("active");
      }
    },
    /**
     * will consider relevant if at least one nuts from the programme is contained in the selected region or its children
     * ex: for RO31: RO31, RO312 will be relevant, but not RO, RO3, RO4 nor RO32
     */
    isRelevantForSelectedRegion(programme) {
      const region = this.filters.region;
      if (!region) return true;

      for (const nutsItem of programme.nuts) {
        if (this.isAncestorRegion(region, nutsItem)) {
          return true;
        }
      }
      return false;
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.programmes {
  li {
    list-style-type: none;
    color: inherit;
  }

  small {
    color: #898989;
  }

  .programme-list {
    padding-left: 1.6rem;
    color: #444;
  }

  .programme-sublist-wrapper {
    display: none;
  }

  .flag {
    box-shadow: 0 0 2px #757575;
  }
  .active .programme-sublist-wrapper {
    display: block;
  }

  .programme-sublist {
    padding-left: 0;
    margin-left: 2rem;
  }

  .programme-sublist-item {
    margin: 1rem 0;
  }

  .programme-item {
    list-style-type: square;
    color: #56bafc;
    a {
      color: #444;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }

  .title-wrapper:hover .title {
    text-decoration: underline;
  }

  a.programme-sublist-item:hover {
    &:before {
      text-decoration: none;
    }
  }

  .flag {
    width: 30px;
    height: 20px;
    img {
      width: 100%;
    }
  }

  .ind-count {
    display: inline;
    font-size: 2rem;
    color: black;
  }

  .title {
    color: #444;
    font-weight: bold;
    font-size: 1.2rem;
  }

  .programme-item {
    margin: 1rem 0;
    font-size: 1.3rem;
  }

  .programme-list {
    display: none;
  }

  .programme-list.active {
    display: block;
  }

  .title-wrapper > * {
    display: inline-block;
    margin-right: 0.5rem;
  }

  .title-wrapper {
    -js-display: flex;
    display: flex;
    cursor: pointer;
    align-items: center;
    margin: 1rem 0;
  }

  .country_thumbnail {
    display: inline-block;
    width: 24px;
    margin-right: 0.5rem;
  }
}
</style>
