/*
 * First, import all country flags as svg sprites,
 * using webpack's svg-sprite-loader.
 */

import _COUNTRIES from 'js/constants/countries.json5';

export const COUNTRIES = {};
export const DONORS = _COUNTRIES.donors;
export const BENEFICIARIES = _COUNTRIES.beneficiaries;

for (const code in DONORS) {
  COUNTRIES[code] = Object.assign({type: "donor"}, DONORS[code]);
}
for (const code in BENEFICIARIES) {
  COUNTRIES[code] = Object.assign({type: "beneficiary"}, BENEFICIARIES[code]);
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


function get_longest_name(obj) {
  return d3.values(obj).reduce( (longest, item) => (
    longest.length > item.name.length ? longest : item.name
  ) );
}

export default {
  beforeCreate() {
    this.DONORS = DONORS;
    this.BENEFICIARIES = BENEFICIARIES;
    this.COUNTRIES = COUNTRIES;
  },

  data() {
    return {
      longestCountry: get_longest_name(this.COUNTRIES),
      longestBeneficiary: get_longest_name(this.BENEFICIARIES),
    };
  },

  computed: {
    // this can be used by components displaying per-beneficiary data.
    // (although it's sad that each component should run this code. TODO?)
    beneficiarydata() {
      // filter dataset by everything except beneficiary
      const _filters = d3.keys(this.filters)
                         .filter((f) => f != 'beneficiary');
      const dataset = this.filter(this.dataset, _filters);
      const aggregated = this.aggregate(
        dataset,
        ['beneficiary', 'fm'],
        [
          'allocation',
          //'bilateral_allocation',
          'project_count',
          //'project_count_positive',
          //'project_count_ended',
          //{source: 'sector', destination: 'sectors', type: String},
        ],
        false
      );

      // base the data on the beneficiary list from constants
      const out = {}
      for (const bid in this.BENEFICIARIES) {
        const item = {
          allocation: {},
          project_count: {},
          total: 0,
          //sectors: d3.set(),
        };

        Object.assign(item, this.BENEFICIARIES[bid]);

        const data = aggregated[bid];
        for (const fm in data) {
          const d = data[fm],
                allocation = d.allocation,
                project_count = d.project_count;

          item.total += allocation;
          item.allocation[fm] = allocation;
          item.project_count[fm] = project_count;
        }

        // skip 0-valued items for now
        if (item.total == 0) continue;

        out[bid] = item;
      }

      return out;
    },
  },

  methods: {
    isBeneficiary(d) {
      return this.BENEFICIARIES[d.id] !== undefined;
    },
    isDonor(d) {
      return this.DONORS[d.id] !== undefined;
    },

    toggleBeneficiary(b, etarget) {
      // don't filter by zero-valued items
      if (b.total == 0) return;

      this.filters.beneficiary = this.filters.beneficiary == b.id ?
                                 null : b.id;
    },

    get_flag_name(c) { return get_flag_name(c) },
    get_country_name(c) { return get_country_name(c)},
  },
};
