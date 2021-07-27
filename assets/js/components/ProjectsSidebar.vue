<template>
  <sidebar :class="classNames" :embedded="embedded">
    <embeddor tag="sidebar" />
    <xsummary :initial="dataset" :embedded="embedded"></xsummary>

    <tabs cache-lifetime="">
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
import BaseSidebar from "./BaseSidebar";

import Summary from "./ProjectsSummary";
import News from "./ProjectsNews";
import Projects from "./Projects";
import Embeddor from "./includes/Embeddor";

export default {
  components: {
    Embeddor,
    xsummary: Summary,
    news: News,
    projects: Projects,
  },
  extends: BaseSidebar,

  props: {
    projectsDatasource: String,
  },
};
</script>
