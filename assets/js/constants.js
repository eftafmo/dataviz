"use strict";

import FMs from 'js/constants/financial-mechanisms.json5';

const FMColours = {};
for(let fm in FMs) {
  FMColours[fm] = FMs[fm].colour;
}

export {FMColours};
