<template>
<div class="donor-programmes">
 <table v-for="items in data">
   <thead>
     <th>{{items.donor}} organizations</th>
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
import BaseMixin from './Base';

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
      const dataset = this.dataset;
      const donor_states = [];
      let donors = {}
      let donors_map = new Set();

      for (let d of dataset) {

        if (donor_states.indexOf(d.donor) === -1) {
          donor_states.push(d.donor);
          donors[donor_states.indexOf(d.donor)] = {
            donor: d.donor,
            donor_programme_partners: [],
            countries: [],
            programmes: []
          }
        }

        for (let p in d.donor_programme_partners) {
          let temp = donors_map.has(p)
          if (temp == false) {
            donors_map.add(p)
            donors_map[p] = d.donor_programme_partners[p]
            donors_map[p].donor = d.donor
          } else {
            for (let x of d.donor_programme_partners[p].programmes) {
              if (donors_map[p].programmes.indexOf(x) === -1)
                donors_map[p].programmes.push(x)
              if (donors[donor_states.indexOf(d.donor)].programmes.indexOf(x) === -1)
                donors[donor_states.indexOf(d.donor)].programmes.push(x)
            }
            for (let x of d.donor_programme_partners[p].states) {
              if (donors_map[p].states.indexOf(x) === -1)
                donors_map[p].states.push(x)
              if (donors[donor_states.indexOf(d.donor)].countries.indexOf(x) === -1)
                donors[donor_states.indexOf(d.donor)].countries.push(x)
            }
            if (donors_map[p].donor == donors[donor_states.indexOf(d.donor)].donor) {
              if (donors[donor_states.indexOf(d.donor)].donor_programme_partners.indexOf(donors_map[p]) === -1)
                donors[donor_states.indexOf(d.donor)].donor_programme_partners.push(donors_map[p]);
            }
          }
        }
      }

      return donors
    },
  },

});

</script>
