"use strict";

require("../css/main.css");

require("../js/header.js");
require("../js/footer.js");

// register polyfills
import './lib/polyfills';

// register widget components
import './widgets/index.js';

// expose root vue instances globally
require("expose-loader?root!./root-instances.js");

// also expose components, because embedding
require("expose-loader?$dataviz!./components/index");

// vue globally-installed plugins
import Vue from 'vue';
import VueSuper from 'vue-super';
Vue.use(VueSuper);

//keep homepage layout as a one column layout
if(document.querySelector('.homepage_content_wrapper')) {
  let main = document.querySelector('.homepage_content_wrapper').parentNode;
  main.style.display = 'block'
}
