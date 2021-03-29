"use strict";

require("./css/main.css");

require("./js/header");
require("./js/footer");

//register widget components
import "./js/widgets";

//expose root vue instances globally
require("expose-loader?root!./js/root-instances");
//expose search stuff globally
require("expose-loader?search!./js/search");
