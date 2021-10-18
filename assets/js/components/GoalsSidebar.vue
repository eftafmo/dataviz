<template>
  <sidebar :class="classNames" :embedded="embedded">
    <embeddor :period="period" tag="sidebar" />

    <tabs cache-lifetime="">
      <tab name="Results">
        <results
          class="sidebar-content"
          :initial="dataset"
          :embedded="embedded"
          hide-sector
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

import Programmes from "./Programmes";
import Embeddor from "./includes/Embeddor";
import Results from "./Results";

export default {
  components: {
    Embeddor,
    results: Results,
    programmes: Programmes,
  },
  extends: BaseSidebar,
};
</script>
