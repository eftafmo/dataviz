"use strict";

require("../css/main.css");

require("../js/header.js");

// register polyfills
import './lib/polyfills';

// register widget components
import './widgets/index.js';

// expose root vue instances globally
require("expose-loader?root!./root-instances.js");

//keep homepage layout as a one column layout
if(document.getElementById('overview')) {
  let main = document.getElementById('overview').parentNode;
  main.style.display = 'block'
}
