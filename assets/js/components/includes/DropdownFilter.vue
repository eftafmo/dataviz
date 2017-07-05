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
    top: 30px;
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
    @media (max-width: 600px){
      top: 8px;
      width: 100%;
      right: 4px;
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
