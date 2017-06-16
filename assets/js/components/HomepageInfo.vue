<template>
<div v-if="hasData" class="info-viz">

<!-- <div  class="circle-wrapper"> -->
    <div class="circle">
      <div class="programmes-count"><span>{{data.programmes_total}}</span><br>Programmes</div>
      <div class="projects-count"><span>{{data.projectcount}}</span><br>Projects</div>
    </div>
    <div class="line-wrapper">
      <div class="donor-count"><span>3</span> Donor states</div>
      <div class="states-count"><span>{{data.beneficiaries.length}}</span> Beneficiary states</div>
  </div>
 <!-- </div> -->
  <div class="total-spent"><h1>{{format(data.allocation_total)}}</h1>
    <h3>spent on</h3>
  </div>
  <div class="overview-info">to reduce social and economic disparities across europe and to strenghten bilateral relations</div>
</div>
</template>


<style lang="less">
.info-viz {

  .donor-count, .states-count {
    word-spacing: 30rem;
    text-align: center;
    max-width: 150px;
    span {
      font-weight: bold;
    }
    font-size: 1.7rem;
  }


  .donor-count {
    margin-left: 15%;
  }

  .states-count {
    margin-right: 8%;
  }

  .line-wrapper {
    display: flex;
    justify-content: space-between;
    position: absolute;
    top: 40%;
    z-index: -1;
    width: 100%;
  }

  .total-spent {
    position: absolute;
    top: 1rem;
    left: 45%;
    text-align: center;
  }

  .overview-info {
    position: absolute;
    left: 38%;
    text-align: center;
    max-width: 350px;
    font-size: 2rem;
    bottom: 9%;
  }

  .circle-wrapper {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: absolute;
    top: 0;
    font-size: 3rem;
    text-align: center;
  }
    .circle {
    span {
      font-weight: bold;
      font-size: 4.5rem;
    }
    background: rgba(251, 251, 251, 0.86);
    padding: 6rem 7rem;
    border-radius: 116rem;
    border: 4px solid white;
    z-index: 1;
    text-align: center;
    position: absolute;
    top: 30%;
    left: 39%;
    font-size: 3rem;

    }

  .legend {
    cursor: pointer;
    position: relative;
    z-index: 1;
    .fm span {
      width: 10px; height: 10px;
      display: inline-block;
    }
    li {
      list-style-type: none;
      display: inline-block;
      margin-right: 2rem;
    }
    .fm {
      transition: all .5s ease;
      display: block;
    }
    .fm.disabled {
      filter: grayscale(100%);
      opacity: 0.5;
    }

    .fm.selected {
      text-shadow: 0 0 1px #999;
    }
  }
}
</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';

import BaseMixin from './mixins/Base';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';
import {mydata} from './dummy.js'


export default Vue.extend({
  mixins: [
    BaseMixin, WithFMsMixin, WithCountriesMixin
  ],


  computed: {
    data () {
      const dataset = this.filter(mydata);
      const beneficiaries = {};

      for (const d of dataset) {
        let beneficiary = beneficiaries[d.beneficiary];
        if (beneficiary === undefined)
          beneficiary = beneficiaries[d.beneficiary] = {
          };
      }

      const out = {
        beneficiaries: [],
        projectcount: 0,
        programmes_total: 0,
        allocation_total: 0,
      };

      for (const b in beneficiaries) {
        const programmes = beneficiaries[b],
              beneficiary = {
                id: b,
              };

        out.beneficiaries.push(beneficiary);
      }

      //getting unique programmes
      let programmes = []
      for (const d of dataset) {
        out.projectcount += d.project_count;
          for (const b of out.beneficiaries) {
              if(d.beneficiary == b.id){
                 for (let p of d.programmes){
                  programmes.push(p)
                 }
              }
          }
      }
      let unique = programmes.filter(function(elem, index, self) {
             return index == self.indexOf(elem);
      })
      out.programmes_total = unique.length

      //allocation total
      for (let d of dataset) {
        out.allocation_total += parseInt(d.allocation);
      }

      //Sort by country
      out.beneficiaries.sort((a,b) => d3.ascending(a.id,b.id));
      return out;
    },
  },
});
</script>
