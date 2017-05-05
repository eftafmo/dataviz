<template>
  <select @change="setFilter">
    <option value="">
      {{ title }}
    </option>
    <option
        v-for="(item, id, index) in items"
        :value="item.id"
        :selected="item.id == current"
    >
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
    @media (max-width: 600px){
      top: 8px;
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
  },
});

</script>
