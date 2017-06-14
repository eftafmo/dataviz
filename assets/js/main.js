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


document.addEventListener("DOMContentLoaded", function(event) {
// expand function for sidebar on mobile
if (window.matchMedia("(max-width: 768px)").matches) {
  let sidebar = document.querySelector('.sidebar');
  sidebar.addEventListener('click', function(e){
    let close_button = this.querySelector('#close-sidebar .icon');
    if (e.target == close_button) {
     this.classList.remove('is-expanded-on-mobile');
    }
    else {
      this.classList.add('is-expanded-on-mobile');
    }
  })
}
});
