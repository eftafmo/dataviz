"use strict";

import 'normalize.css'
require("../css/main.css");

require("../js/header.js");

// register widget components
import './widgets/index.js';

// expose components globally
require("expose-loader?components!./components/index.js");

// expose vue globally
// TODO: in a cleaner way?
import Vue from 'vue';
window.Vue = Vue;


import './components/SidebarResultTab.vue';
// we import the default export from app modules,
import SidebarResults from "./SidebarResults.vue";

// and instantiate and target them specifically.
new SidebarResults({
  el: '#sidebar-results',
});
