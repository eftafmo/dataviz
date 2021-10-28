<template>
  <div :class="classNames">
    <embeddor :period="period" tag="project_partners" />
    <slot v-if="!embedded" name="title"></slot>
    <table>
      <thead>
        <tr>
          <th>Donor State</th>
          <th>Organisations</th>
          <th>Countries</th>
          <th>Programmes</th>
          <th>Projects</th>
        </tr>
      </thead>
      <tbody v-for="item in data" :key="item.donor">
        <tr class="section_header" @click="show_items($event)">
          <td>{{ get_country_name(item.donor) }}</td>
          <td>{{ item.organizations.length }}</td>
          <td>{{ item.countries.size }}</td>
          <td>{{ item.programmes.size }}</td>
          <td>{{ item.projects.size }}</td>
        </tr>
        <tr
          v-for="organization in item.organizations"
          :key="organization.id"
          class="section_item"
        >
          <td colspan="2">
            <a :href="organization.url" target="_blank">
              {{ organization.name }}
            </a>
          </td>
          <td>{{ organization.countries.size }}</td>
          <td>{{ organization.programmes.size }}</td>
          <td>{{ organization.projects }}</td>
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
          <th>
            {{ allProjects.size }}
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
import Embeddor from "./includes/Embeddor";
import { sum } from "../lib/util";

export default {
  components: { Embeddor },
  extends: Component,
  type: "donor-projects",

  mixins: [PartnersMixin, CountriesMixin],

  data() {
    return {};
  },

  computed: {
    searchPageBaseUrl() {
      const url = new URL("/search/project/", window.location);
      if (this.period) {
        url.searchParams.append("period", this.period);
      }
      if (this.filters.fm) {
        url.searchParams.append("financial_mechanism_ss", this.filters.fm);
      }
      if (this.currentBeneficiary) {
        url.searchParams.append("state_name", this.currentBeneficiary.name);
      }
      if (this.filters.sector) {
        url.searchParams.append("priority_sector_ss", this.filters.sector);
      }
      if (this.filters.area) {
        url.searchParams.append("programme_area_ss", this.filters.area);
      }
      return url;
    },
    data() {
      if (!this.hasData) return [];

      const dataset = this.filtered;
      const out = {};

      for (let d of dataset) {
        // only count rows having donor project partners
        if (Object.keys(d.PJDPP).length === 0) continue;
        let item = out[d.donor];
        if (item === undefined) {
          item = out[d.donor] = {
            donor: d.donor,
            countries: new Set(),
            programmes: new Set(),
            projects: new Set(),
            organizations: {},
          };
        }
        item.countries.add(d.beneficiary);
        item.programmes.add(d.programme);
        for (const prj_code in d.projects) {
          item.projects.add(prj_code);
        }
        for (let org_id in d.PJDPP) {
          let org = item.organizations[org_id];
          if (!org) {
            const orgName = d.PJDPP[org_id]["name"];
            const url = new URL(this.searchPageBaseUrl, window.location);
            url.searchParams.append("organisation", orgName);

            org = item.organizations[org_id] = {
              id: org_id,
              countries: new Set(),
              programmes: new Set(),
              projects: 0,
              name: orgName,
              url: url.toString(),
            };
          }
          org.countries.add(d.beneficiary);
          org.programmes.add(d.programme);
          org.projects += d.PJDPP[org_id]["prj"];
        }
      }

      const donors = [];
      for (let donor in out) {
        // convert main dict to array
        const orgs = [];
        for (let org_id in out[donor].organizations) {
          // convert organisations dict to array and sort
          orgs.push(out[donor].organizations[org_id]);
        }
        out[donor].organizations = orgs;
        orgs.sort((a, b) => d3.ascending(a.name, b.name));
        donors.push(out[donor]);
      }
      const $this = this;
      donors.sort((a, b) =>
        d3.ascending(
          $this.get_sort_order(a.donor),
          $this.get_sort_order(b.donor)
        )
      );
      return donors;
    },
    allOrganizations() {
      return new Set(
        this.data.map((item) => item.organizations.map((org) => org.id)).flat()
      );
    },
    allCountries() {
      return new Set(
        this.data.map((item) => Array.from(item.countries)).flat()
      );
    },
    allProgrammes() {
      return new Set(
        this.data.map((item) => Array.from(item.programmes)).flat()
      );
    },
    allProjects() {
      return new Set(this.data.map((item) => Array.from(item.projects)).flat());
    },
  },

  methods: {
    sum,
    show_items(e) {
      let target = e.target.parentNode.parentNode;
      target.classList.toggle("active");
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.donor-projects {
  width: 100%;
  @media (max-width: 800px) {
    overflow: auto;
  }
  table {
    border-collapse: collapse;

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
      max-width: 214px;
    }
    th {
      color: #333;
      font-size: 14px;
      font-weight: normal;
      white-space: nowrap;
    }
    td {
      color: #666;
      font-size: 13px;
    }

    tr {
      border: 1px solid transparent;
    }

    tr.section_item:hover td {
      cursor: default;
      //border-top:1px solid #50b9ff;
      //border-bottom:1px solid #50b9ff;
      //&:first-of-type{
      //border-left:1px solid #50b9ff;
      //}
      //&:last-of-type {
      //border-right:1px solid #50b9ff;
      //}
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
        border-bottom: 2px solid #eee;
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
