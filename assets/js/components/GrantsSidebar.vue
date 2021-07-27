<template>
  <sidebar :class="classNames" :embedded="embedded">
    <embeddor tag="sidebar" />
    <xsummary :initial="dataset" :embedded="embedded"></xsummary>

    <tabs cache-lifetime="">
      <tab name="Results">
        <results
          class="sidebar-content"
          :initial="dataset"
          :embedded="embedded"
        ></results>
      </tab>
      <tab name="Programmes">
        <programmes
          class="sidebar-content"
          :initial="dataset"
          :embedded="embedded"
        ></programmes>
      </tab>
    </tabs>
  </sidebar>
</template>

<script>
import BaseSidebar from "./BaseSidebar";

import Summary from "./Summary";
import Results from "./Results";
import Programmes from "./Programmes";
import Embeddor from "./includes/Embeddor";

export default {
  components: {
    Embeddor,
    xsummary: Summary,
    results: Results,
    programmes: Programmes,
  },
  extends: BaseSidebar,
};
</script>
