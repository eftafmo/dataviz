<template>
<transition v-if="onMobile" name="fade">
  <div class="mobileTooltip">
  <span @click="$emit('destroyTooltip')" class="close-btn">x</span>
  <ul>
      <li class="list-header">
          <svg class="flag">
                <use :xlink:href="`#${get_flag_name(data.id)}`"></use>
          </svg>
          {{data.id}}
      </li>
      <li>
          <b>{{data.sectors.size()}}</b> {{singularize('sectors', data.sectors.size())}}
      </li>
      <li>
          <b>{{data.areas.size()}}</b> {{singularize('programme areas' , data.areas.size())}}
      </li>
      <li>
          <b>{{data.programmes.size()}}</b> {{singularize('programmes', data.programmes.size())}}
      </li>
  </ul>
  </div>
</transition>
</template>


<style lang="less">
.mobileTooltip{
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 99999;
  background: white;
  .close-btn {
    position: absolute;
    right: 10px;
    top: 5px;
  }
  .fade-enter-active, .fade-leave-active {
  transition: opacity .5s
  }
  .fade-enter, .fade-leave-to{
    opacity: 0
  }

  padding: .1rem 1rem;
  box-shadow: 0px 0px 3px #aaa;
  ul {
    list-style-type: none;
    padding-left: 0;
    font-size: 1.5rem;
    margin: 1rem 0;
  }

  li {
    font-size: 1.7rem;
  }

  .list-header {
    margin-bottom: .3rem;
    border-bottom: 1px solid #eee;
  }

  .flag {
    box-shadow: 0px 0px 2px #757575;
    display: inline-block;
    width: 30px;
    height: 20px;
  }
}

</style>


<script>
import Vue from 'vue';

import ComponentMixin from '../mixins/Component.js'
import {FILTERS} from '../mixins/WithFilters'
import WithCountriesMixin, {COUNTRIES, get_flag_name} from '../mixins/WithCountries';

export default Vue.extend({
  mixins: [ComponentMixin,WithCountriesMixin],

  props: {
    data: Object,
  },

  data() {
    return {
      onMobile: false,
    }
  },
  created () {
    // Add a media query listener handle mobile events
    var mq = window.matchMedia ('(max-width: 768px)');
    var $this = this;
    mq.addListener(function(mq) { $this.onMobile = mq.matches; });
    this.onMobile = mq.matches; // initial check;
  },

})
</script>
