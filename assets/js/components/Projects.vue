<template>
  <programmes :datasource="datasource" :initial="initial" class="projects">
    <template #programme-content="x">
      <projects
        :id="x.programme.programme_code"
        :details-datasource="detailsDatasource"
        :country="x.beneficiary.id"
        :sector="x.programme.sector"
        :name="x.programme.programme_name"
        :extra="extra"
      ></projects>
    </template>
  </programmes>
</template>

<script>
import Component from "./Component";

import Programmes from "./Programmes";
import Projects from "./includes/Projects";
import ProjectsMixin from "./mixins/Projects";

export default {
  components: {
    programmes: Programmes,
    projects: Projects,
  },
  extends: Component,
  mixins: [ProjectsMixin],

  props: {
    detailsDatasource: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      extra: null,
    };
  },
};
</script>

<style lang="less">
.dataviz .viz.programmes.projects {
  .programme-item {
    list-style-type: none;
  }
  .programme-list {
    padding-left: 0.5rem;
  }
  .title {
    font-weight: 400;
  }
}
</style>
