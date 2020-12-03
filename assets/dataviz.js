"use strict";

// load styles
require("./css/dataviz.less")

// register polyfills
import './js/lib/polyfills'

// install vue global plugins
import Vue from 'vue'
import VueSuper from 'vue-super'
Vue.use(VueSuper)


// register sentry if production environment
import Raven from 'raven-js';
import RavenVue from 'raven-js/plugins/vue';

if (process.env.NODE_ENV === "production") {
  console.info("Running in production mode! Enabling Sentry.");

  Raven
    .config(window._dv_sentry_config.dsn, {
      environment: window._dv_sentry_config.environment
    })
    .addPlugin(RavenVue, Vue)
    .install();
}
else {
  console.info("Development mode, no sentry.");
}

// and expose components, because embedding
require("expose-loader?$dataviz!./js/components/index")
