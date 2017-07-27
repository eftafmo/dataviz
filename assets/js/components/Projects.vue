<template>
<programmes :datasource="datasource" :initial="initial" class="projects">
  <template slot="programme-content" scope="x">
    <projects
        :country="x.beneficiary.id"
        :sector="x.programme.sector"
        :id="x.programme.programme_code"
        :name="x.programme.programme_name"
    ></projects>
  </template>
</programmes>
</template>


<style lang="less">
.projects {
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


<script>
import Vue from 'vue';

import ComponentMixin from './mixins/Component';
import Programmes from './Programmes';
import Projects from './includes/Projects'


export default Vue.extend({
  mixins: [
    ComponentMixin,
  ],
  components: {
    programmes: Programmes,
    projects: Projects,
  },
});
</script>
