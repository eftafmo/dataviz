<template>
<ul class="programmes" v-if="hasData">
  <li v-for="beneficiary in data.beneficiaries">
    <div class="content-item programmes_content">
      <div class="body">
        <div @click="toggleContent($event)" class="title-wrapper">
          <div class="flag">
            <svg class="flag">
              <use :xlink:href="`#${get_flag_name(beneficiary.id)}`"></use>
            </svg>
          </div>
          <h3 class="title">{{ get_country_name(beneficiary.id) }}</h3>
          <small>({{ beneficiary.programmes.length }} programmes)</small>
        </div>
        <ul class="programme-list" :class="[{ active : filters.beneficiary }]">
          <li v-for="programme in beneficiary.programmes" class="programme-item">
            <slot name="programme-content" :programme="programme" :beneficiary="beneficiary">
              <a class="programme-sublist-item" target="_blank" :href=programme.programme_url> {{ programme.programme_name }} </a>
            </slot>
          </li>
        </ul>
      </div>
    </div>
  </li>
</ul>
</template>


<style lang="less">
.programmes{
  li {
    list-style-type: none;
    color: inherit;
  }

  small {
    color: #898989;
  }

  .programme-list {
    padding-left: 1.6rem;
    color: #444;
  }

  .programme-sublist-wrapper {
    display: none;
  }

  .active .programme-sublist-wrapper     {
    display: block;
  }

  .programme-sublist {
    padding-left: 0;
    margin-left: 2rem
  }

  .programme-sublist-item {
    margin: 1rem 0;
  }

  .programme-item {
    list-style-type: square;
    color: #56bafc;
    a{
      color: #444;
    }
  }

  .title-wrapper:hover .title{
    text-decoration: underline;
  }

  a.programme-sublist-item:hover{
    &:before {
    text-decoration: none;
    }
  }

  .flag {
    width: 30px;
    height: 20px;
    img {
        width: 100%;
    }
  }

  .ind-count {
    display: inline;
    font-size: 2rem;
    color: black;
  }

  .title {
    color: #444;
    font-weight: bold;
    font-size: 1.2rem;
  }

  .programme-item {
    margin: 1rem 0;
    font-size: 1.3rem;
  }

  .programme-list {
    display: none;
  }

  .programme-list.active {
    display: block;
  }


  .title-wrapper > * {
    display: inline-block;
    margin-right: .5rem;
  }

  .title-wrapper {
    display: flex;
    cursor: pointer;
    align-items: center;
    margin: 1rem 0;
  }

  .country_thumbnail {
    display: inline-block;
    width: 24px;
    margin-right: .5rem;
  }
}
</style>


<script>
import * as d3 from 'd3';

import Component from './Component';
import WithCountriesMixin, {COUNTRIES, get_flag_name} from './mixins/WithCountries';


export default Component.extend({
  mixins: [
    WithCountriesMixin,
  ],

  updated() {
    //TODO: this can be done a lot better
    if (window.matchMedia("(max-width: 800px)").matches) {
      const parent_nav = this.$el.parentNode.parentNode.parentNode.querySelector('[aria-controls="#programmes"]');
      if (!parent_nav) return;
      parent_nav.innerHTML = 'Programmes ('+this.data.projectcount+')'
    }
  },

  computed: {

    data() {
      const dataset = this.filtered;
      const beneficiaries = {};
      let totalcount = 0;
      let programmes_array = [];

      for (const d of dataset) {
        const programmes = d.programmes;

        if (!programmes || !Object.keys(programmes).length) continue;

        let beneficiary = beneficiaries[d.beneficiary];
        if (beneficiary === undefined)
          beneficiary = beneficiaries[d.beneficiary] = {
            _projectcount: 0,
          };

        for (const p in programmes) {
          // TODO: clean the project count logic
          const projectcount = 0;
          //const projectcount = +programmes[p];
          //if (projectcount == 0) continue;
          let programme = beneficiary[p];
          if (programme === undefined)
            programme = beneficiary[p] = {
              sector: d.sector,
              programme_code: p,
              programme_name: programmes[p].name,
              programme_url: programmes[p].url,
            };
        }
      }

      const out = {
        beneficiaries: [],
        projectcount: totalcount,
      };

      for (const b in beneficiaries) {
        const programmes = beneficiaries[b],
              beneficiary = {
                id: b,
                programmes: [],
              };
        out.beneficiaries.push(beneficiary);
        for (const p in programmes) {
          if(programmes[p].programme_code)
            out.projectcount += 1;
          const value = programmes[p];
          if (p === '_projectcount') {
            beneficiary.projectcount = value;
            continue;
          }
          beneficiary.programmes.push(value);
        }
        // Sort by programme code, the Tripartite programme always last
        beneficiary.programmes.sort((a,b) => d3.ascending(
          a.programme_code.replace('IN22', 'ZZZZ'),
          b.programme_code.replace('IN22', 'ZZZZ')
        ));
      }

      //Sort by country
      out.beneficiaries.sort((a,b) => d3.ascending(this.get_country_name(a.id),this.get_country_name(b.id)));
      return out;
    },
  },

  methods: {
    toggleContent(e) {
      //remove comment if you want to toggle between elements

      // let all_programe_items = this.$el.querySelectorAll('.programme-item');
      // for (let item of all_programe_items){
      //     if(item.classList.contains('active'))
      //         item.classList.remove('active')
      // }

      //TODO : get rid of the parenNode logic
      let target;
      if (e.target.parentNode.classList.contains('flag'))
        target = e.target.parentNode.parentNode.parentNode.querySelector('.programme-list');
      else
         target = e.target.parentNode.parentNode.querySelector('.programme-list');
      if(target.classList.contains('active')){
        target.classList.remove('active')
      }
      else {
        target.classList.add('active')
      }
    },
  },
});
</script>
