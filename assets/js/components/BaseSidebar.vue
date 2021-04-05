<script>
import Component from './Component'

import Sidebar from './includes/Sidebar'
import { Tabs, Tab } from 'vue-tabs-component'

export default Component.extend({
  components: {
    sidebar: Sidebar,
    tabs: Tabs,
    tab: Tab
  }
})
</script>
