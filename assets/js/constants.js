"use strict";

import FMs from 'js/constants/financial-mechanisms.json5';

const FMColours = {};
for(let fm in FMs) {
  FMColours[fm] = FMs[fm].colour;
}

import Sectors from 'js/constants/priority-sectors.json5';
const SectorColours = {};
for (let sector of Sectors) {
  SectorColours[sector.name] = sector.colour;
}

export {FMColours, SectorColours};
