<template>
  <select @change="getIndex(items)">
  <option v-bind="title">
  {{title}}
  </option>
    <option :id="item.id" v-for="(item, id, index) in items">
       {{item.name}}
    </option>
  </select>
</template>

<style lang="less">
  select {
    position: absolute;
    top: 30px;
    right: 0;
    border-color: #fff;
    background: #fff;
    color: #aaa;
    &:focus {
      outline: none;
    }
    option {
      color: black;
    }
  }
</style>

<script>
import Vue from 'vue';
import {FILTERS} from '../global/filters.js'

export default Vue.extend({

  props: {
    items: {
      id: String,
      name: String,
    },
    title: String,
    filters: String,
  },

  methods: {
    getIndex(items){
      var select = event.target;
      var selected_opt = select.options[select.selectedIndex].id;
      var filter = select.getAttribute('filter');
      FILTERS[filter] = selected_opt
      console.log(selected_opt);
    }
  },


});

</script>
