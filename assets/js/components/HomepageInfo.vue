<template>
<div v-if="hasData" class="info-viz">
   <div class="total-spent">
      <h1>{{format(data.allocation_total)}}</h1>
      <h3>spent on</h3>
   </div>
<!-- <div  class="circle-wrapper"> -->
    <div class="circle">
      <div class="programmes-count">
        <span>{{data.programmes_total}}</span><br>Programmes
      </div>
      <div class="projects-count">
        <span>{{data.projectcount}}</span><br>Projects
      </div>
    </div>
    <div class="line-wrapper">
      <div class="donor-count">
        <span class="mobile_only">FROM</span>
        <span>3</span> Donor states
      </div>
      <div class="states-count">
        <span class="mobile_only">TO</span>
        <span>{{data.beneficiaries.length}}</span> Beneficiary states
      </div>
  </div>
 <!-- </div> -->

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
    margin-bottom: 3rem;
    @media (min-width:768px) and (max-width:1000px){
      top: auto;
      bottom: 0;
      > div {
        margin: 0;
      }
    }
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
    @media (min-width:768px) and (max-width:1400px){
      left: 42%;
      text-align: center;
      max-width: 200px;
      font-size: 1.5rem;
      bottom: 9%;
    }
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
    @media (min-width:768px) and (max-width:1400px){
      top: 33%;
      left: 40%;
      font-size: 2rem;
      padding: 4rem 5rem;
      span {
        font-size: 3.5rem;
      }
    }


    }
    //mobile
    @media(max-width:768px) {
      padding-top: 1rem;
      border-top: 1px solid #ddd;
      .circle,
      .line-wrapper,
      .total-spent,
      .overview-info {
        position: static;
      }
      //square in this case
      .circle {
        background: rgb(35, 97, 146);
        border-radius: 0;
        color: white;
        padding: 1rem;
        margin: 2rem;
        max-width: 327px;
        margin-left: auto;
        margin-right: auto;
      }

      .donor-count, .states-count, .overview-info {
        margin: 0;
        max-width: none;
      }

      .overview-info {
        margin-bottom: 2rem;
        border-top: solid #236192;
        padding-top: 1rem;
      }

      .total-spent h1{
        display: inline-block;
        color: #236192;
        border-bottom: solid #236192;
        margin: 0;
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


export default Vue.extend({
  mixins: [
    BaseMixin, WithFMsMixin, WithCountriesMixin
  ],


  computed: {
    data () {
      const dataset = this.filter(this.dataset);
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
        console.log(d.allocation)
        out.allocation_total += parseFloat(d.allocation);
      }

      //Sort by country
      out.beneficiaries.sort((a,b) => d3.ascending(a.id,b.id));
      return out;
    },
  },
});
</script>
