import * as Vue from 'vue/dist/vue.esm-bundler.js'
import Tabs from 'vue3-tabs-component/src/components/Tabs.vue';
import Tab from 'vue3-tabs-component/src/components/Tab.vue';
import $super from './js/lib/vue-super.js'
import * as Dataviz from './js/root-instances.js'


function createApp(spec) {
  const app = Vue.createApp(spec)

  app
    .component('tabs', Tabs)
    .component('tab', Tab)

  app.config.globalProperties.$super = $super

  return app
}

window._createApp = createApp
window.Dataviz = Dataviz
