<template>
<sidebar :class="classNames" :embedded="embedded">
  <xsummary
      :initial="dataset"
      :embedded="embedded"
  ></xsummary>

  <tabs cache-lifetime="">
    <tab name="Results">
      <results
          class="sidebar-content"
          :initial="dataset"
          :embedded="embedded"
      ></results>
    </tab>
    <tab name="News">
      <news
          class="sidebar-content"
          :initial="dataset"
          :embedded="embedded"
      ></news>
    </tab>
    <tab name="Projects">
      <projects
          class="sidebar-content"
          :initial="dataset"
          :details-datasource="projectsDatasource"
          :embedded="embedded"
      ></projects>
    </tab>
  </tabs>
</sidebar>
</template>


<script>
import BaseSidebar from './BaseSidebar'

import Summary from './PartnersSummary'
import Results from './PartnersResults'
import News from './PartnersNews'
import Projects from './PartnersProjects'


export default BaseSidebar.extend({
  components: {
    xsummary: Summary,
    results: Results,
    news: News,
    projects: Projects,
  },
  props: {
    projectsDatasource: String,
  },
})
</script>
