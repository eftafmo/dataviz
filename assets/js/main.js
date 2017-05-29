"use strict";

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


//keep homepage layout as a one column layout
if(document.getElementById('overview')) {
  let main = document.getElementById('overview').parentNode;
  main.style.display = 'block'
}
