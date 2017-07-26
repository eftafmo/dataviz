<template>
  <select class="viz-select" @change="setFilter">
    <option value="">
      {{ title }}
    </option>
    <option
        v-for="(item, id, index) in items"
        :value="getFilterName(item)"
        :selected="getFilterName(item) == current"
    >
      {{item.name}}
    </option>
  </select>
</template>

<style lang="less">
  .viz-select {
    position: absolute;
    top: -4rem;
    @media (min-width: 1400px) {
      top: -6.4rem;
    }
    right: 0;
    border-color: #fff;
    background: #fff;
    color: #aaa;
    font-family: inherit;
    &:focus {
      outline: none;
    }
    option {
      color: black;
    }

    @media (max-width: 950px){
    position: relative;
    float: initial;
    top: 0;
    right: initial;
    display: block;
    margin-bottom: 1rem;
    margin-top:-1rem;
    }
  }

  .dropdown {
    @media (max-width: 950px) {
      width: 100%;
    }
  }

</style>

<script>
import Vue from 'vue';
import {FILTERS} from '../../globals.js'

export default Vue.extend({

  props: {
    items: {
      id: String,
      name: String,
    },
    title: String,
    filter: String,
  },

  computed : {
    current() {
      return FILTERS[this.filter];
    },
  },

  methods: {
    setFilter(e) {
      const select = e.target;
      FILTERS[this.filter] = select.value || null;
    },

    getFilterName(item){
      //special case for beneficiary filter
      if(this.filter == 'beneficiary'){
        return item.id
      }
      else {
        return item.name
      }
    },

  },
});

</script>
