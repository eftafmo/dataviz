<template>
<div v-if="hasData" class="donor-programmes">
 <h2>{{title}}</h2>
 <table v-for="item in data">
   <thead>
     <th>{{get_country_alt_name(item.donor)}} organizations</th>
     <th>Countries ({{item.countries.size()}})</th>
     <th>Programmes ({{item.programmes.size()}})</th>
   </thead>
   <tbody>
     <tr v-for="org in item.organizations">
       <td>{{org.name}}</td>
       <td>{{org.countries.size()}}</td>
       <td>{{org.programmes.size()}}</td>
     </tr>
   </tbody>
 </table>
</div>
</template>

<style lang="less">
.donor-programmes {
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
      title: "Donor programme partners",
    }
  },

  computed: {
    data() {
      const dataset = this.filtered;
      const out = {}

      for (let d of dataset) {
        let item = out[d.donor];
        if (item === undefined && Object.keys(d.donor_programme_partners).length > 0 ) {
          item = out[d.donor] = {
            donor: d.donor,
            countries: d3.set(),
            programmes: d3.set(),
            organizations: {},
          }
        }
        for (let org_id in d.donor_programme_partners) {
          let org = item.organizations[org_id]
          const org_data = d.donor_programme_partners[org_id]
          if (org == undefined) {
            org = item.organizations[org_id] = {
              countries: d3.set(),
              programmes: d3.set(),
              name: org_data.name
            }
          }
          for (let state of org_data.states) {
            item.countries.add(state);
            org.countries.add(state);
          }
          for (let prg of org_data.programmes) {
            item.programmes.add(prg);
            org.programmes.add(prg);
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
