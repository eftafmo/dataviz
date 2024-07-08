import _COUNTRIES from "@js/constants/countries.json5";

export const COUNTRIES = {};
export const DONORS = _COUNTRIES.donors;
export const BENEFICIARIES = _COUNTRIES.beneficiaries;
export const PARTNERS = _COUNTRIES.partners;

const _types = {
  donor: DONORS,
  beneficiary: BENEFICIARIES,
  partner: PARTNERS,
};

const flags = import.meta.glob("../../../sprites/flags/*.png", { eager: true });

function transformCountryName(name) {
  return name.toLowerCase().replace(/ /g, "");
}

Object.entries(_types).forEach(([type, source]) => {
  Object.entries(source).forEach(([code, country], index) => {
    const flagName = `flag-${transformCountryName(source[code].name)}.png`;

    COUNTRIES[code] = {
      type,
      // In dev this will be the URL to the flag, however in prod this will
      // be a DATA URI string. Making the sprites easily embeddable in SVG
      // elements.
      flag: flags["../../../sprites/flags/" + flagName].default,
      flagName,
      sortOrder: index + 1,
      ...country,
    };
  });
});

export function get_flag(code) {
  if (code.length > 2 && code !== "Intl") {
    // because Intl is a country and has a flag
    code = code.substring(0, 2);
  }
  const country = COUNTRIES[code];
  if (!country) throw "Country not found: " + code;

  return country.flag;
}

export function get_country_name(code) {
  const country_name = COUNTRIES[code].name;
  if (!country_name) throw "Country not found: " + code;
  return country_name;
}

export function get_sort_order(code) {
  const sort_order = COUNTRIES[code].sortOrder;
  if (!sort_order) throw "Country not found: " + code;
  return sort_order;
}

function get_longest_name(obj) {
  return Object.values(obj).reduce((longest, item) =>
    longest.length > item.name.length ? longest : item.name,
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
    allCountries() {
      const result = {};
      this.COUNTRY_ARRAY.forEach((country) => (result[country.id] = country));
      return result;
    },
    COUNTRY_ARRAY() {
      return Object.values(this.COUNTRIES).filter(
        (country) =>
          !country.periods ||
          !this.period ||
          country.periods.indexOf(this.period) !== -1,
      );
    },
    allBeneficiaries() {
      const results = {};
      Object.values(this.BENEFICIARIES).forEach((country, index) => {
        results[country.name] = {
          ...country,
          sortOrder: index,
        };
      });
      return Object.values(results);
    },
    BENEFICIARY_ARRAY() {
      return Object.values(this.BENEFICIARIES).filter(
        (country) =>
          !country.periods ||
          !this.period ||
          country.periods.indexOf(this.period) !== -1,
      );
    },
    currentBeneficiary() {
      return (
        this.filters &&
        this.filters.beneficiary &&
        this.BENEFICIARY_ARRAY.find(
          (country) => country.id === this.filters.beneficiary,
        )
      );
    },
  },
  methods: {
    isBeneficiary(d) {
      return this.BENEFICIARIES[d.id] !== undefined;
    },
    isDonor(d) {
      return this.DONORS[d.id] !== undefined;
    },
    toggleBeneficiary(b, allowHungary = false) {
      if (!allowHungary && this.isHungaryException(b.id)) return;
      // don't filter by zero-valued items
      if (b.total === 0) return;

      this.filters.beneficiary =
        this.filters.beneficiary === b.id ? null : b.id;
    },
    toggleDonor(d) {
      if (d.total === 0) return;

      this.filters.donor = this.filters.donor === d.id ? null : d.id;
    },
    // TODO: Refactor to use camelCase here.
    get_flag,
    get_country_name,
    get_sort_order,
  },
};
