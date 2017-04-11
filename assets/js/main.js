"use strict";

require("../css/normalize.css");
require("../css/main.css");

require("../js/header.js");

// we import component modules only for side effects (tag registration).
import './components/Tag.vue';
import './components/SidebarResultTab.vue';
// we import the default export from app modules,
import SidebarResults from "./SidebarResults.vue";

// and instantiate and target them specifically.
new SidebarResults({
  el: '#sidebar-results',
});

// but we might want to do instantiation in the template,
// so we need to expose stuff globally
require("expose-loader?Mechanisms!./modules/Mechanisms.vue");
require("expose-loader?Sectors!./modules/Sectors.vue");
