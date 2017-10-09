"use strict";

// load styles
require("./css/dataviz.less")

// register polyfills
import './js/lib/polyfills'

// install vue global plugins
import Vue from 'vue'
import VueSuper from 'vue-super'
Vue.use(VueSuper)

// and expose components, because embedding
require("expose-loader?$dataviz!./js/components/index")
