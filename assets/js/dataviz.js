"use strict";

// register polyfills
import './lib/polyfills';

// vue globally-installed plugins
import Vue from 'vue';
import VueSuper from 'vue-super';
Vue.use(VueSuper);

require("../css/dataviz.less");

// also expose components, because embedding
require("expose-loader?$dataviz!./components/index");
