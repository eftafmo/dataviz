<template>
<div v-if="hasData" class="donor-programmes">
 <h2>{{title}}</h2>
 <table>
   <thead>
     <th>Donor state</th>
     <th>Organisations</th>
     <th>Countries</th>
     <th>Programmes</th>
   </thead>
   <tbody v-for="item in data">
     <tr @click="show_items($event)" class="section_header">
       <td>{{get_country_name(item.donor)}}</td>
       <td>{{item.organizations.length}}</td>
       <td>{{item.countries.size()}}</td>
       <td>{{item.programmes.size()}}</td>
     </tr>
     <tr class="section_item hidden" v-for="organizations in item.organizations">
      <td colspan="2">{{organizations.name}}</td>
      <!-- <td>  </td> -->
      <td>{{organizations.countries.size()}}</td>
      <td>{{organizations.programmes.size()}}</td>
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
  .hidden {
    display: none;
  }
  .active {
    th:first-of-type:before {
      transform: rotate(90deg);
    }
  }

  table  {
    border-collapse: collapse;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
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

    tr.section_item:hover td{

      border-top:2px solid #50b9ff;
      border-bottom:2px solid #50b9ff;
      &:first-of-type{
       border-left:2px solid #50b9ff;
      }
      &:last-of-type {
        border-right:2px solid #50b9ff;
      }
    }

    .section_item.hidden {
      display: none;
    }

    .active {
      td{
        &:before{
          transform:rotate(90deg)
        }
      }
    }

    .section_header {
      font-weight: bold;
      cursor: pointer;
      color: black;
      td{
        position: relative;
        &:first-of-type {
          padding-left: 13px!important;
          &:before {
          content: "\25BA";
          margin-right: .5rem;
          transition: all 300ms;
          font-size: 1.1rem;
          position: absolute;
          left: 0;
          top: 6px;
          }
        }
      }
    }

    thead {
       border-spacing: 4px;


      th{
        //TODO: Make this work
        // border-bottom: 2px solid #eee;
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

  methods: {
    show_items(e){
      let target = e.target.parentNode.parentNode;
      target.classList.toggle('active')
      let dest = target.querySelector('.section_item');
      if(dest.classList)
        dest.classList.toggle('hidden')
    }
  },

});

</script>
