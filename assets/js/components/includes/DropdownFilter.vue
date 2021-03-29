<template>
  <select class="viz-select clearfix" @change="setFilter">
    <option value="">
      {{ title }}
    </option>
    <option
      v-for="(item, id, index) in items"
      :value="getFilterName(item)"
      :selected="getFilterName(item) == current"
      :key="id"
    >
      {{ item.name }}
    </option>
  </select>
</template>

<style lang="less">
.dataviz .viz-select {
  border-color: #fff;
  background: #fff;
  color: #aaa;
  font-family: inherit;
  max-width: 100%;
  margin-bottom: 2rem !important;
  &:focus {
    outline: none;
  }
  option {
    color: black;
  }
  @media (min-width: 780px) and (max-width: 1000px) {
    width: 100%;
  }
}

.dropdown {
  @media (max-width: 950px) {
    width: 100%;
  }
}
</style>

<script>
import Vue from "vue";

import WithFiltersMixin from "../mixins/WithFilters";

export default Vue.extend({
  mixins: [WithFiltersMixin],

  props: {
    items: {
      id: String,
      name: String,
    },
    title: String,
    filter: String,
  },

  computed: {
    current() {
      return this.filters[this.filter];
    },
  },

  methods: {
    setFilter(e) {
      const select = e.target;
      this.filters[this.filter] = select.value || null;
    },

    getFilterName(item) {
      // special case for country filters
      if (this.filter == "beneficiary" || this.filter == "donor") {
        return item.id;
      } else {
        return item.name;
      }
    },
  },
});
</script>
