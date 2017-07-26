<template>
<div class="donor-programmes">
 <table v-for="items in data">
   <thead>
     <th>{{items.donor_state}} organizations</th>
     <th>countries ({{items.countries.length}})</th>
     <th>programmes ({{items.programmes.length}})</th>
   </thead>
   <tbody>
     <tr v-for="progammes in items.donor_programme_partners">
       <td>{{progammes.name}}</td>
       <td>{{progammes.states.length}}</td>
       <td>{{progammes.programmes.length}}</td>
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
import BaseMixin from './mixins/Base';
import {FILTERS} from '../globals.js'

export default Vue.extend({
  mixins: [
    BaseMixin,
  ],

  data(){
    return {
      item: Object,
    }
  },

  computed: {
    data() {
      const dataset = this.filtered;
      const donor_states = [];
      let donors = {}
      let donors_map = new Map();
      let programmes = [];

      for (let d of dataset) {
        if(donor_states.indexOf(d.donor_state) === -1){
          donor_states.push(d.donor_state);
        }
        if(Object.keys(d.donor_programme_partners).length != 0)
        programmes.push(d.donor_programme_partners)
        for (let p in d.donor_programme_partners) {
                    let temp = donors_map.get(d.donor_programme_partners[p].name)
                    if(temp == undefined) {
                      temp = donors_map.set(p , d.donor_state)
                    }
        }
      }


      console.log(donors_map)

      for (let d in donor_states) {
       donors[d] = {
          donor_state : donor_states[d],
          donor_programme_partners :[],
          countries : [],
          programmes: []
        }
      }

      donors_map.forEach(function(value,key){
        for (let d in donors) {
          if(donors[d].donor_state == value) {
            donors[d].donor_programme_partners.push({id: key, name: null, states:[], programmes: []})
          }
        }
      })


      for (let a of programmes) {
        for (let b in a ) {
          for (let c in donors){
            for (let d in donors[c].donor_programme_partners) {
              if (b == donors[c].donor_programme_partners[d].id){
                donors[c].donor_programme_partners[d].name = a[b].name
                for(let e of a[b].states){
                  if(donors[c].donor_programme_partners[d].states.indexOf(e) === -1){
                    donors[c].donor_programme_partners[d].states.push(e)
                    if(donors[c].countries.indexOf(e)===-1)
                       donors[c].countries.push(e);
                }
                for(let e of a[b].programmes){
                  if(donors[c].donor_programme_partners[d].programmes.indexOf(e) === -1){
                     donors[c].donor_programme_partners[d].programmes.push(e)
                       if(donors[c].programmes.indexOf(e)===-1)
                       donors[c].programmes.push(e);
                    }
                  }
                }
              }
            }
          }
        }
      }

      return donors
    },
  },

});

</script>
