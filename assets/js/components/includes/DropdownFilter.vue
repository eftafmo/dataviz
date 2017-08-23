<template>
  <select class="viz-select clearfix" @change="setFilter">
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
    float: right;
    border-color: #fff;
    background: #fff;
    color: #aaa;
    -webkit-appearance: none;
    font-family: inherit;
    max-width: 100%;
    &:focus {
      outline: none;
    }
    option {
      color: black;
    }

    @media (max-width: 950px){
      float: initial;
      margin-bottom: 4rem;
      display: block;
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
      // special case for country filters
      if (this.filter == 'beneficiary' || this.filter == 'donor'){
        return item.id
      }
      else {
        return item.name
      }
    },

  },
});

</script>
