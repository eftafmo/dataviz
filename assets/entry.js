import * as Vue from "vue/dist/vue.esm-bundler.js";
import $super from "./js/lib/vue-super.js";
import * as Dataviz from "./js/root-instances.js";
import { setMergeStrategy } from "./js/components/Component";
import { Tab, Tabs } from "vue3-tabs-component";

function createApp(...args) {
  const app = Vue.createApp(...args);

  app.component("Tabs", Tabs).component("tab", Tab);

  app.config.globalProperties.$super = $super;

  setMergeStrategy(app);

  return app;
}

window._createApp = createApp;
window.Dataviz = Dataviz;
