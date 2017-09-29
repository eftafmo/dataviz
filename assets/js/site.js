"use strict";

require("../css/main.css");

require("../js/header.js");
require("../js/footer.js");


//register widget components
import './widgets/index.js';

//expose root vue instances globally
require("expose-loader?root!./root-instances.js");
//expose search stuff globally
require("expose-loader?search!./search.js");
