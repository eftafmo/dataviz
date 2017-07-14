<template>
<programmes :datasource="datasource" :initial="initial">
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

<script>
import Vue from 'vue';

import BaseMixin from './mixins/Base';
import Programmes from './Programmes';
import Projects from './includes/Projects'


export default Vue.extend({
  mixins: [BaseMixin],
  components: {
    programmes: Programmes,
    projects: Projects,
  },
});
</script>
