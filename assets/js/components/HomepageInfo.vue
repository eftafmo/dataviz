<template>
<div v-if="hasData" class="info-viz">

<div  class="circle-wrapper">
    <div class="circle">
      <div class="programmes-count"><span>{{data.programmes_total}}</span><br>Programmes</div>
      <div class="projects-count"><span>{{data.projectcount}}</span><br>Projects</div>
    </div>
    <div class="line-wrapper">
      <div class="donor-count"><span>3</span> Donor states</div>
      <div class="states-count"><span>{{data.beneficiaries.length}}</span> Beneficiary states</div>
  </div>
 </div>
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
    span {
      font-weight: bold;
      font-size: 4.5rem;
    }
    .circle {
      background: rgba(251, 251, 251, 0.86);
      padding: 6rem 7rem;
      border-radius: 100rem;
      border: 4px solid white;
      margin-left: 5rem;
      margin-top: 2rem;
      z-index: 1;
    }
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
// import {mydata} from './dummy.js'


export default Vue.extend({
  mixins: [
    BaseMixin, WithFMsMixin, WithCountriesMixin
  ],


  computed: {
    data () {
      const dataset = this.filter(this.dataset);
      const beneficiaries = {};
      let totalcount = 0;
      let allocation_total = 0;

      for (const d of dataset) {
        const programmes = d.programmes;

        if (!programmes) continue;

        let beneficiary = beneficiaries[d.beneficiary];
        if (beneficiary === undefined)
          beneficiary = beneficiaries[d.beneficiary] = {
            _projectcount: 0,
          };

        for (const p in programmes) {
          const projectcount = +programmes[p];

          if (projectcount == 0) continue;

          let programme = beneficiary[p];
          if (programme === undefined)
            programme = beneficiary[p] = {
              sector: d.sector,
              projectcount: 0,
            };

          programme.projectcount += projectcount;
          beneficiary._projectcount += projectcount;
          totalcount += projectcount;
        }
      }

      let programmes_total = 0;
      const out = {
        beneficiaries: [],
        projectcount: totalcount,
        programmes_total: programmes_total,
        allocation_total: allocation_total,
      };

      for (const b in beneficiaries) {
        const programmes = beneficiaries[b],
              beneficiary = {
                id: b,
                programmes: [],
              };

        out.beneficiaries.push(beneficiary);

        for (const p in programmes) {
          const value = programmes[p];
          if (p === '_projectcount') {
            beneficiary.projectcount = value;
            continue;
          }
          beneficiary.programmes.push(Object.assign({name: p}, value));
        }
      }

      for (let d of out.beneficiaries){
        out.programmes_total += d.programmes.length
      }


      for (let d of dataset) {
        out.allocation_total += parseInt(d.allocation);
      }

      //Sort by country
      out.beneficiaries.sort((a,b) => d3.ascending(a.id,b.id));
      return out;
    },
  },

  methods: {

    handleFilter() {
      return
    },

  },
});
</script>
