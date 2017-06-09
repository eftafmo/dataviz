import Vue from 'vue';

import BaseMixin from './components/mixins/Base';
import * as components from './components/index';


export default Vue.extend({
  name: 'Grants',
  mixins: [BaseMixin],

  components: {
    mechanisms: components.Mechanisms,
    sectors: components.Sectors,
    xmap: components.Map,
    beneficiaries: components.Beneficiaries,
    sidebar: components.Sidebar,
    globalfilters: components.GlobalFilters,
  },
});
