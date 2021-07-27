import _COUNTRIES from "@js/constants/countries.json5";
import { getAssetUrl } from "../../lib/util";

export const COUNTRIES = {};
export const DONORS = _COUNTRIES.donors;
export const BENEFICIARIES = _COUNTRIES.beneficiaries;
export const PARTNERS = _COUNTRIES.partners;

const _types = {
  donor: DONORS,
  beneficiary: BENEFICIARIES,
  partner: PARTNERS,
};
for (const t in _types) {
  const source = _types[t];

  for (const code in source) {
    COUNTRIES[code] = Object.assign({ type: t }, source[code]);
  }
}

export function get_flag_name(code) {
  if (code.length > 2 && code != "Intl") {
    // because Intl is a country and has a flag
    code = code.substring(0, 2);
  }
  const country = COUNTRIES[code];
  if (!country) throw "Country not found: " + code;
  const flag = country.name.toLowerCase().replace(/ /g, "");
  return `flag-${flag}`;
}

export function get_country_name(code) {
  const country_name = COUNTRIES[code].name;
  if (!country_name) throw "Country not found: " + code;
  return country_name;
}

export function get_country_alt_name(code) {
  const country_name = COUNTRIES[code].alt_name;
  if (!country_name) throw "Country not found: " + code;
  return country_name;
}

export function get_sort_order(code) {
  const sort_order = COUNTRIES[code].sort_order;
  if (!sort_order) throw "Country not found: " + code;
  return sort_order;
}

function get_longest_name(obj) {
  return Object.values(obj).reduce((longest, item) =>
    longest.length > item.name.length ? longest : item.name
  );
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
      longestDonor: get_longest_name(this.DONORS),
      longestBeneficiary: get_longest_name(this.BENEFICIARIES),
    };
  },

  computed: {
    // TODO: make the constants arrays, and the objects pre-computed
    COUNTRY_ARRAY() {
      return Object.values(this.COUNTRIES);
    },
    BENEFICIARY_ARRAY() {
      return Object.values(this.BENEFICIARIES);
    },
  },

  methods: {
    isBeneficiary(d) {
      return this.BENEFICIARIES[d.id] !== undefined;
    },
    isDonor(d) {
      return this.DONORS[d.id] !== undefined;
    },
    toggleBeneficiary(b) {
      // don't filter by zero-valued items
      if (b.total == 0) return;

      this.filters.beneficiary = this.filters.beneficiary == b.id ? null : b.id;
    },
    toggleDonor(d) {
      if (d.total == 0) return;

      this.filters.donor = this.filters.donor == d.id ? null : d.id;
    },
    // TODO: Refactor to use camelCase here.
    get_flag_url(c) {
      return getAssetUrl(
        `sprites/flags/${this.get_flag_name(c)}.png`,
        this.origin || this.$.root.props.origin
      );
    },
    get_flag_name(c) {
      return get_flag_name(c);
    },
    get_country_name(c) {
      return get_country_name(c);
    },
    get_country_alt_name(c) {
      return get_country_alt_name(c);
    },
    get_sort_order(c) {
      return get_sort_order(c);
    },
  },
};
