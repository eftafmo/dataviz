<template>
<div class="donor-programmes">
 <slot name="title" v-if="!this.embedded"></slot>
 <dropdown v-if="isReady" filter="DPP" title="No filter selected" :items="dropdown_items"></dropdown>
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
     <tr
      class="section_item"
      hidden="true"
      v-for="organization in item.organizations"
      :class="{active_filter : filters.DPP == organization.name}"
      @click="toggleDPP($event, organization.name)"
     >
      <td colspan="2">{{organization.name}}</td>
      <td>{{organization.countries.size()}}</td>
      <td>{{organization.programmes.size()}}</td>
     </tr>
   </tbody>
 </table>
</div>
</template>

<style lang="less">
.dataviz .donor-programmes {
  width: 100%;
  @media(max-width: 800px){
    overflow: auto;
  }

  //fallback for ie
  [hidden="hidden"] {
    display: none;
  }

  [hidden="false"] {
    display: table-row;
  }

  .active {
    th:first-of-type:before {
      transform: rotate(90deg);
    }
  }

  .active_filter {
    background: #eee;
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
      font-size: 14px;
      white-space: nowrap;
      font-weight: normal;
    }
    td {
      color: #666;
      font-size: 13px;
    }

    tr {
        border:1px solid transparent;
        cursor: pointer;
    }

    tr.section_item:hover td{

      border-top:1px solid #50b9ff;
      border-bottom:1px solid #50b9ff;
      &:first-of-type{
       border-left:1px solid #50b9ff;
      }
      &:last-of-type {
        border-right:1px solid #50b9ff;
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
import Component from './Component';
import PartnersMixin from './mixins/Partners';
import CountriesMixin from './mixins/WithCountries';
import Dropdown from './includes/DropdownFilter';

export default Component.extend({
  mixins: [
    PartnersMixin,
    CountriesMixin,
  ],

  components: {
    'dropdown': Dropdown,
  },

  data(){
    return {
    }
  },

  created() {
    // need to re-remove dpp from filters, because it's re-added
    // by PartnersMixin. silly.
    const col = "DPP"
    const idx = this.filter_by.indexOf(col)
    if (idx !== -1)
      this.filter_by.splice(idx, 1)
  },

  computed: {
    data() {
      if (!this.hasData) return []

      const dataset = this.filtered;
      const out = {}

      for (let d of dataset) {
        // only count rows having donor programme partners
        if (!d.DPP) continue;
        let item = out[d.donor];
        if (item === undefined ) {
          item = out[d.donor] = {
            donor: d.donor,
            countries: d3.set(),
            programmes: d3.set(),
            organizations: {},
          }
        }
        item.countries.add(d.beneficiary);
        item.programmes.add(d.programme);
        if (item.organizations[d.DPP] == undefined) {
          item.organizations[d.DPP] = {
              name: d.DPP,
              countries: d3.set(),
              programmes: d3.set()
          }
        }
        item.organizations[d.DPP].countries.add(d.beneficiary);
        item.organizations[d.DPP].programmes.add(d.programme);
      }

      const donors = [];
      for (let donor in out) {
        // convert organisations dict to array and sort
        const orgs = []
        const partners = Object.keys(out[donor].organizations).sort()
        for (let partner of partners) {
          orgs.push(out[donor].organizations[partner])
        }
        out[donor].organizations = orgs;
        donors.push(out[donor]);
      }
      const $this = this;
      donors.sort((a,b) => d3.ascending(
          $this.get_sort_order(a.donor),
          $this.get_sort_order(b.donor)
      ));
      return donors
    },

    dropdown_items(){
    let organizations = {};
      for (let items of this.data){
        for(let org of items.organizations){
           let item = organizations[org.name] = {
            name: org.name
          }
        }
      }
      return organizations
    },
  },

  methods: {
    handleFilterDPP(organisation) {
      this.filters.DPP == organisation ? false : true
    },

    toggleDPP(e, organisation) {
      this.filters.DPP = this.filters.DPP == organisation ? null : organisation;
    },

    show_items(e){
      let target = e.target.parentNode.parentNode
      target.classList.toggle('active')
      let dest = target.querySelectorAll('.section_item');
      for (let t in dest){
        try {
          if(dest[t].getAttribute('hidden') == 'hidden')
            dest[t].setAttribute('hidden','false')
          else
            dest[t].setAttribute('hidden','hidden')
        }
        catch (e) {
          return null;
        }
      }
    }
  },

});

</script>
