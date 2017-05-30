"use strict";
import {slugify} from 'js/lib/util';

import FMs from 'js/constants/financial-mechanisms.json5';
const FMColours = {};
for(let fm in FMs) {
  FMColours[fm] = FMs[fm].colour;
}

// TODO: this functionality is duplicated in components/mixins/WithSectors,
// so remove from here.
import Sectors from 'js/constants/priority-sectors.json5';
const SectorColours = {};
for (let sector of Sectors) {
  SectorColours[slugify(sector.name)] = sector.colour;
}

export {FMColours, SectorColours};
