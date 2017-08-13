<template>
<div v-if="hasData" class="donor-projects">
 <h2>{{title}}</h2>
 <table>
   <thead>
     <th>Donor state</th>
     <th>Organizations</th>
     <th>Countries</th>
     <th>Programmes</th>
     <th>Projects</th>
   </thead>
   <tbody>
     <tr v-for="item in data">
       <td>{{get_country_alt_name(item.donor)}}</td>
       <td>{{item.organizations.length}}</td>
       <td>{{item.countries.size()}}</td>
       <td>{{item.programmes.size()}}</td>
       <td>{{item.projects.size()}}</td>
     </tr>
   </tbody>
 </table>
</div>
</template>

<style lang="less">
.donor-projects {
  width: 100%;
  @media(max-width: 800px){
    overflow: auto;
  }
  table  {
    border-collapse: collapse;

    width: 100%;
    * {
      text-align: left;
    }
    thead th,
    tbody td {
      width: 21%;
      text-align: right;
      padding: 5px;
    }
    th {
      color: #333;
      font-size: 13px;
      white-space: nowrap;
    }
    td {
      color: #666;
      font-size: 12px;
    }

    tr {
        border:2px solid transparent;
    }

    tr:hover td{

      border-top:2px solid #50b9ff;
      border-bottom:2px solid #50b9ff;
      &:first-of-type{
       border-left:2px solid #50b9ff;
      }
      &:last-of-type {
        border-right:2px solid #50b9ff;
      }
    }

    thead {
       border-spacing: 4px;


      th{
        border-bottom: 2px solid #eee;
      }
    }

    thead th:first-of-type,
    tbody tr td:first-of-type {
      width: 58%;
      text-align: left;
    }
  }
}
</style>

<script>

import Vue from 'vue';
import * as d3 from 'd3';
import BaseMixin from './Base';
import PartnersMixin from './mixins/Partners';
import CountriesMixin from './mixins/WithCountries';

export default Vue.extend({
  mixins: [
    BaseMixin,
    PartnersMixin,
    CountriesMixin,
  ],

  data(){
    return {
      title: "Donor project partners",
    }
  },

  computed: {
    data() {
      const dataset = this.filtered;
      const out = {}

      for (let d of dataset) {
        let item = out[d.donor];
        if (item === undefined && Object.keys(d.donor_project_partners).length > 0 ) {
          item = out[d.donor] = {
            donor: d.donor,
            countries: d3.set(),
            programmes: d3.set(),
            projects: d3.set(),
            organizations: {},
          }
        }
        for (let org_id in d.donor_project_partners) {
          let org = item.organizations[org_id]
          if (org == undefined) {
            org = item.organizations[org_id] = {
              countries: d3.set(),
              programmes: d3.set(),
              projects: d3.set(),
              name: d.donor_project_partners[org_id]
            }
          }
          for (let state in d.dpp_states) {
            item.countries.add(state);
            org.countries.add(state);
          }
          for (let prg in d.dpp_programmes) {
            item.programmes.add(prg);
            org.programmes.add(prg);
          }
          for (let prj in d.dpp_projects) {
            item.projects.add(prj);
            org.projects.add(prj);
          }
        }
      }
      const donors = [];
      for (let donor in out) {
        // convert main dict to array
        const orgs = []
        for (let org_id in out[donor].organizations) {
          // convert organisations dict to array and sort
          orgs.push(out[donor].organizations[org_id]);
        }
        out[donor].organizations = orgs;
        orgs.sort((a,b) => d3.ascending(a.name, b.name));
        donors.push(out[donor]);
      }
      const $this = this;
      donors.sort((a,b) => d3.ascending(
          $this.get_sort_order(a.donor),
          $this.get_sort_order(b.donor)
      ));
      return donors
    },
  },

});

</script>