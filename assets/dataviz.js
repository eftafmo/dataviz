"use strict";


// register polyfills
import * as Sentry from '@sentry/vue';
import Vue from 'vue';
import VueSuper from 'vue-super';
import './js/lib/polyfills';

Vue.use(VueSuper)
if (import.meta.env.NODE_ENV === "production" && window._dv_sentry_config) {
  console.info("Running in production mode! Enabling Sentry.");

  Sentry.init({
    Vue: Vue,
    dsn: window._dv_sentry_config.dsn,
    enviroment: window._dv_sentry_config.environment
  })

}
else {
  console.info("Development mode, no sentry.");
}

// and expose components, because embedding
// !! // require("expose-loader?$dataviz!./js/components/index")

import './js/components/index'
