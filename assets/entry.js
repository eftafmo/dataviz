import * as Vue from "vue/dist/vue.esm-bundler.js";
import Tabs from "vue3-tabs-component/src/components/Tabs.vue";
import Tab from "vue3-tabs-component/src/components/Tab.vue";
import $super from "./js/lib/vue-super.js";
import * as Dataviz from "./js/root-instances.js";
import { setMergeStrategy } from "./js/components/Component";

function createApp(...args) {
  const app = Vue.createApp(...args);

  app.component("Tabs", Tabs).component("tab", Tab);

  app.config.globalProperties.$super = $super;

  setMergeStrategy(app);

  return app;
}

window._createApp = createApp;
window.Dataviz = Dataviz;
