"use strict";

require("../css/normalize.css");
require("../css/main.css");

require("../js/header.js");

import * as d3 from "d3";
import {sankey as d3_sankey} from "d3-sankey";
import Vue from "vue";
import SidebarResults from "./SidebarResults.vue";

import MainApp from './MainApp.vue';

new Vue({
  el: '#content',
  render: h => h(MainApp)
});
