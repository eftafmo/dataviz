<template>
  <div :class="classNames">
    <embeddor :period="period" tag="programme_partners" />
    <slot v-if="!embedded" name="title"></slot>
    <dropdown
      v-if="isReady"
      filter="DPP"
      title="No filter selected"
      :items="dropdown_items"
    ></dropdown>
    <table>
      <thead>
        <tr>
          <th>Donor State</th>
          <th>Organisations</th>
          <th>Countries</th>
          <th>Programmes</th>
        </tr>
      </thead>
      <tbody v-for="item in data" :key="item.donor">
        <tr class="section_header" @click="show_items($event)">
          <td>{{ get_country_name(item.donor) }}</td>
          <td>{{ item.organizations.length }}</td>
          <td>{{ item.countries.size }}</td>
          <td>{{ item.programmes.size }}</td>
        </tr>
        <tr
          v-for="organization in item.organizations"
          :key="organization.name"
          class="section_item"
          :class="{ active_filter: filters.DPP == organization.name }"
          @click="toggleDPP($event, organization.name)"
        >
          <td colspan="2">{{ organization.name }}</td>
          <td>{{ organization.countries.size }}</td>
          <td>{{ organization.programmes.size }}</td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <th>Total</th>
          <th>
            {{ allOrganizations.size }}
          </th>
          <th>
            {{ allCountries.size }}
          </th>
          <th>
            {{ allProgrammes.size }}
          </th>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script>
import * as d3 from "d3";
import Component from "./Component";
import PartnersMixin from "./mixins/Partners";
import CountriesMixin from "./mixins/WithCountries";
import Dropdown from "./includes/DropdownFilter";
import Embeddor from "./includes/Embeddor";
import { sum } from "../lib/util";

export default {
  components: {
    Embeddor,
    dropdown: Dropdown,
  },
  extends: Component,
  type: "donor-programmes",

  mixins: [PartnersMixin, CountriesMixin],

  data() {
    return {};
  },

  computed: {
    data() {
      if (!this.hasData) return [];

      const dataset = this.filtered;
      const out = {};

      for (let d of dataset) {
        // only count rows having donor programme partners
        if (!d.DPP) continue;
        let item = out[d.donor];
        if (item === undefined) {
          item = out[d.donor] = {
            donor: d.donor,
            countries: new Set(),
            programmes: new Set(),
            organizations: {},
          };
        }
        item.countries.add(d.beneficiary);
        item.programmes.add(d.programme);
        if (item.organizations[d.DPP] == undefined) {
          item.organizations[d.DPP] = {
            name: d.DPP,
            countries: new Set(),
            programmes: new Set(),
          };
        }
        item.organizations[d.DPP].countries.add(d.beneficiary);
        item.organizations[d.DPP].programmes.add(d.programme);
      }

      const donors = [];
      for (let donor in out) {
        // convert organisations dict to array and sort
        const orgs = [];
        const partners = Object.keys(out[donor].organizations).sort();
        for (let partner of partners) {
          orgs.push(out[donor].organizations[partner]);
        }
        out[donor].organizations = orgs;
        donors.push(out[donor]);
      }
      const $this = this;
      donors.sort((a, b) =>
        d3.ascending(
          $this.get_sort_order(a.donor),
          $this.get_sort_order(b.donor),
        ),
      );
      return donors;
    },
    dropdown_items() {
      let organizations = {};
      for (let items of this.data) {
        for (let org of items.organizations) {
          let item = (organizations[org.name] = {
            name: org.name,
          });
        }
      }
      return organizations;
    },
    allOrganizations() {
      return new Set(
        this.data
          .map((item) => item.organizations.map((org) => org.name))
          .flat(),
      );
    },
    allCountries() {
      return new Set(
        this.data.map((item) => Array.from(item.countries)).flat(),
      );
    },
    allProgrammes() {
      return new Set(
        this.data.map((item) => Array.from(item.programmes)).flat(),
      );
    },
  },

  created() {
    // need to re-remove dpp from filters, because it's re-added
    // by PartnersMixin. silly.
    const col = "DPP";
    const idx = this.filter_by.indexOf(col);
    if (idx !== -1) this.filter_by.splice(idx, 1);
  },

  methods: {
    sum,
    handleFilterDPP(organisation) {
      this.filters.DPP == organisation ? false : true;
    },

    toggleDPP(e, organisation) {
      this.filters.DPP = this.filters.DPP == organisation ? null : organisation;
    },

    show_items(e) {
      let target = e.target.parentNode.parentNode;
      target.classList.toggle("active");
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.donor-programmes {
  width: 100%;
  @media (max-width: 800px) {
    overflow: auto;
  }

  .active {
    th:first-of-type:before {
      transform: rotate(90deg);
    }
  }

  .active_filter {
    background: #eee;
  }

  table {
    border-collapse: collapse;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
    width: 100%;
    * {
      text-align: left;
    }

    tfoot th,
    thead th,
    tbody td {
      width: 21%;
      text-align: right;
      padding: 5px;
    }
    th {
      color: #333;
      font-size: 14px;
      white-space: nowrap;
      font-weight: normal;
    }
    td {
      color: #666;
      font-size: 13px;
    }

    tr {
      border: 1px solid transparent;
      cursor: pointer;
    }

    tr.section_item:hover td {
      border-top: 1px solid #50b9ff;
      border-bottom: 1px solid #50b9ff;
      &:first-of-type {
        border-left: 1px solid #50b9ff;
      }
      &:last-of-type {
        border-right: 1px solid #50b9ff;
      }
    }

    .section_item {
      display: none;
    }

    .active {
      td {
        &:before {
          transform: rotate(90deg);
        }
      }
      .section_item {
        display: table-row;
      }
    }

    .section_header {
      font-weight: bold;
      cursor: pointer;
      color: black;
      td {
        position: relative;
        &:first-of-type {
          padding-left: 13px !important;
          &:before {
            content: "\25BA";
            margin-right: 0.5rem;
            transition: all 300ms;
            font-size: 1.1rem;
            position: absolute;
            left: 0;
            top: 6px;
          }
        }
      }
    }

    tfoot,
    thead {
      border-spacing: 4px;

      th {
        //TODO: Make this work
        // border-bottom: 2px solid #eee;
      }
    }

    tfoot th:first-of-type,
    thead th:first-of-type,
    tbody tr td:first-of-type {
      width: 58%;
      text-align: left;
    }
  }
}
</style>
