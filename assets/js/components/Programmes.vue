<template>
  <div class="sidebar-tab-pane programmes"
       v-bind:class="{
        'is-selected': selected,
        'is-loading': loading
       }">
    <ul class="sidebar-tab-result-list">
      <li v-for="item in data">
        <div class="sidebar-result-news">
          <div class="body">
            <div class="title-wrapper">
                <div class="flag">
                    <img :src="`/assets/imgs/${get_flag_name(item.beneficiary)}.png`"/>
                </div>
                <h3 class="title">{{ get_country_name(item.beneficiary) }}</h3>
                <small>({{ item.programmes.length }} programmes, {{ item.project_count }} projects)</small>
            </div>
            <ul class="programme-list">
               <li v-for="programme in item.programmes"  class="programme-item">
                  <div  @click="toggleContent($event)" class="programme-item-header"> {{ programme.name }} </div>
                      <div class="programme-sublist-wrapper">
                        <small class="programme-sublist-header">{{ programme.priority_sector }}</small>
                         <ul class="programme-sublist">
                                <li class="programme-sublist-item">
                                        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                                        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                                </li>
                                  <li class="programme-sublist-item">
                                        Lorem ipsum dolor sit amet, consecdsfdolore magna aliqua. Ut enim ad minim veniam,
                                </li>
                                  <li class="programme-sublist-item">
                                        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                                        tempor incididunt ut lasfasfasbore et dolore magna aliqua. Ut enim ad minim veniam,
                                </li>
                                  <li class="programme-sublist-item">
                                        Lorem ipsum dolsfafet dolore magna aliqua. Ut enim ad minim veniam,
                                </li>
                                  <li class="programme-sublist-item">
                                       fasfaliqua. Ut enim ad minim veniam,
                                </li>
                         </ul>
                      </div>
               </li>
               </ul>
          </div>
        </div>
      </li>
    </ul>

    <div class="small muted align-center">
      &ndash;
      <button type="button" class="btn-link">show 10 more results</button>
      |
      <a href="#search" class="muted">show all</a>
      &ndash;
    </div>

  </div>
</template>

<style lang="less">
.programmes{
  li {
    list-style-type: none;
    color: initial;
  }

  .programme-list {
    margin-left: .5rem;
    padding-left: 0;
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

  .programme-sublist-item:before {
    content: "●";
    margin-right: .5rem;
    color: #3D90F3;
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
  }

  .programme-item:before {
    display: inline-block;
    content: "►";
    margin-right: .5rem;
    transition: all 300ms;
  }

  .programme-item {
    margin: 1rem 0;
    font-size: 1.3rem;
  }

  .programme-item-header {
    display: inline;
    cursor: pointer;
  }

  .programme-item.active{
    color: #005494;
    &:before {
        transform: rotate(90deg);
    }
  }

  .title-wrapper > * {
    display: inline-block;
    margin-right: .5rem;
  }

  .title-wrapper {
    display: flex;
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

import Vue from 'vue';
import * as d3 from 'd3';
import BaseMixin from './mixins/Base';
import {SectorColours} from 'js/constants.js';
import WithCountriesMixin, {COUNTRIES, get_flag_name} from './mixins/WithCountries';

export default Vue.extend({
  mixins: [
    BaseMixin, WithCountriesMixin,
  ],

    props: {
      selected: {
        type: Boolean,
        default: false
      },
    },

    watch: {
      selected () { this.loadResults(); }
    },

    data () {
      return {
        loading: false,
        color: SectorColours,
      }
    },

    methods: {
      loadResults() {
        var self = this;
        self.loading = true;

        window.setTimeout(function() {
          // simulate ajax call
          self.loading = false;
        }, 1000);
      },
      toggleContent(e) {
        //remove comment if you want to toggle between elements

        // let all_programe_items = this.$el.querySelectorAll('.programme-item');
        // for (let item of all_programe_items){
        //     if(item.classList.contains('active'))
        //         item.classList.remove('active')
        // }

        const target = e.target.parentNode
        if(target.classList.contains('active')){
            target.classList.remove('active')
        }
        else {
            target.classList.add('active')
        }
      },
    }

  });


</script>
