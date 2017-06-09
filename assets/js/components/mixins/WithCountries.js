/*
 * First, import all country flags as svg sprites,
 * using webpack's svg-sprite-loader.
 */

import _cs from 'js/constants/countries.json5';

export const COUNTRIES = {};
for (const code in _cs.donors) {
  COUNTRIES[code] = Object.assign({type: "donor"}, _cs.donors[code]);
}
for (const code in _cs.beneficiaries) {
  COUNTRIES[code] = Object.assign({type: "beneficiary"}, _cs.beneficiaries[code]);
}

export function get_flag_name(code) {
  const country = COUNTRIES[code];
  if (!country) throw "Country not found: " + code;
  const flag = country.name.toLowerCase().replace(/ /g, '');
  return `flag-${flag}`;
}

export function get_country_name(code) {
  const country_name = COUNTRIES[code].name;
  if (!country_name) throw "Country not found: " + code;
  return country_name;
}

const req = require.context('svg-sprite-loader!imgs', false, /flag-[a-z]+\.png$/);
// we could load all of req.keys() instead, but we want things to fail
// if there's a mismatch between country names and png files.
// (possible TODO: compare req.keys() with countries and warn if necessary)
for (const code in COUNTRIES) {
  req(`./${get_flag_name(code)}.png`);
}

import * as d3 from 'd3';

export default {
  beforeCreate() {
    this.COUNTRIES = COUNTRIES;
  },

  computed: {
    // this can be used by components displaying per-beneficiary data.
    // (although it's sad that each component should run this code. TODO?)
    beneficiarydata() {
      // filter dataset by everything except beneficiary
      const _filters = d3.keys(this.filters)
                         .filter((f) => f != 'beneficiary');
      const dataset = this.filter(this.dataset, _filters);

      const beneficiaries = {}
      for (const d of dataset) {
        const bid = d.beneficiary,
              fm = d.fm,
              value = +d.allocation;

        if (value === 0) continue;

        let beneficiary = beneficiaries[bid];
        if (beneficiary === undefined)
          beneficiary = beneficiaries[bid] = {
            id: bid,
            name: COUNTRIES[bid].name,
            total: 0,
            allocation: {},
            sectors: d3.set(),
          };

        let allocation = beneficiary.allocation[fm];
        if (allocation === undefined)
          allocation = beneficiary.allocation[fm] = 0;

        beneficiary.total += value;
        beneficiary.allocation[fm] = allocation + value;
        beneficiary.sectors.add(d.sector);
      }

      return beneficiaries;
    },
  },

  methods: {
    toggleBeneficiary(b, etarget) {
      this.filters.beneficiary = this.filters.beneficiary == b ?
                                 null : b;
    },
    get_flag_name(c) { return get_flag_name(c) },
    get_country_name(c) { return get_country_name(c)},
  },
};
