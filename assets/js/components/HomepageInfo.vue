<template>
<div v-if="hasData" class="info-viz">
  <div class="heading">
    <p><span class="amount">{{ currency(data.allocation_total) }}</span> spent on</p>
  </div>
  <div class="data-wrapper"><ul class="data">
    <li class="programmes"><span class="amount">{{ number(data.programmes_total) }}</span> Programmes</li>
    <li class="projects"><span class="amount">{{ number(data.projectcount) }}</span> Projects</li>
  </ul></div>
  <div class="ending">
    <p>to reduce social and economic disparities across Europe and to strenghten bilateral relations</p>
  </div>
</div>
</template>


<style lang="less">
.info-viz {
  text-align: center;
  font-size: 2rem;

  p, ul, li {
    margin: 0;
  }

  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  //background-color: rgba(200,200,200,.1);

  span.amount {
    display: block;
    font-weight: bold;
  }

  & > div {
    position: absolute;
    width: 50%;
    left: 25%;
  }

  .heading {
    top: 10%;
    font-size: 1.5em;

    /*
    .amount {
      font-size: 1.2em;
    }
    */
  }

  .data-wrapper {
    width: 40%;
    padding-bottom: 40%;
    left: 30%;
    top: 30%;
    //background-color: rgba(251, 251, 251, 0.8);
    background-image: linear-gradient(rgba(252, 252, 252, .75), rgba(227, 227, 227, .95));
    border: .2em solid white;
    border-radius: 50%;
  }

  .data {
    list-style-type: none;
    padding: 0;

    position: absolute;
    width: 100%;
    left: 50%;
    top: 50%;
    transform: translate(-50%,-50%);

    & > li:not(:last-child) {
      margin-bottom: .5em;
    }

    .programmes {
      font-size: 1.5em;
      line-height: 1.6em;

      .amount {
        font-size: 1.8em;
      }
    }

    .projects {
      font-size: 1em;

      .amount {
        font-size: 2em;
      }
    }
  }

  .ending {
    bottom: 0%;
    font-size: 1.2em;
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
        out.allocation_total += d.allocation;
      }

      //Sort by country
      out.beneficiaries.sort((a,b) => d3.ascending(a.id,b.id));
      return out;
    },
  },
});
</script>
