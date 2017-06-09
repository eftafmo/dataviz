import Vue from 'vue';

import BaseMixin from './components/mixins/Base';
import * as components from './components/index';


export default Vue.extend({
  name: 'Homepage',
  mixins: [BaseMixin],

  components: {
    overview: components.Overview,
  },
});
