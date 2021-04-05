<template>
<programmes :datasource="datasource" :initial="initial" class="projects">
  <template slot="programme-content" scope="x">
    <projects
        :details-datasource="detailsDatasource"
        :country="x.beneficiary.id"
        :sector="x.programme.sector"
        :id="x.programme.programme_code"
        :name="x.programme.programme_name"
        :extra="extra"
    ></projects>
  </template>
</programmes>
</template>

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

<script>
import Component from './Component'

import Programmes from './Programmes'
import Projects from './includes/Projects'
import ProjectsMixin from './mixins/Projects'

export default Component.extend({
  mixins: [
    ProjectsMixin
  ],

  components: {
    programmes: Programmes,
    projects: Projects
  },

  props: {
    detailsDatasource: String
  },

  data () {
    return {
      extra: null
    }
  }
})
</script>
