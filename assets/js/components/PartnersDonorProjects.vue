<template>
<div class="donor-projects">
 <table>
   <thead>
     <th>Donor state</th>
     <th>Organizations</th>
     <th>Countries</th>
     <th>Programmes</th>
     <th>Projects</th>
   </thead>
   <tbody>
     <tr>
       <td>Iceland</td>
       <td>10</td>
       <td>10</td>
       <td>10</td>
       <td>55</td>
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
      item: Object,
    }
  },

  computed: {
    data() {

    },
  },

});

</script>
