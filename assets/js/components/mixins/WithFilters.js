// site-wide navigation filters
export const FILTERS = {
  fm: null,
  beneficiary: null,
  region: null,
  sector: null,
  sdg_no: null,
  area: null,
  donor: null,
  DPP: null,
  thematic: null,
};

// and their usage across scenarios
export const SCENARIOFILTERS = {
  index: ["fm", "beneficiary"],
  funding: ["fm", "beneficiary", "sector", "area", "thematic"],
  global_goals: ["fm", "beneficiary", "sdg_no"],
  cooperation: ["fm", "beneficiary", "sector", "area", "donor", "DPP"],
  projects: ["fm", "beneficiary", "region", "sector", "area"],
  search: ["fm", "beneficiary", "sector", "area", "donor", "DPP"],
  sectors: ["beneficiary"],
  beneficiary_states: ["beneficiary"],
};

// aliases for the backend
SCENARIOFILTERS.grants = SCENARIOFILTERS.funding;
SCENARIOFILTERS.partners = SCENARIOFILTERS.cooperation;
SCENARIOFILTERS.goals = SCENARIOFILTERS.global_goals;
SCENARIOFILTERS.compare = SCENARIOFILTERS.sectors;

const hungaryAllowedScenarios = new Set([
  "index",
  // "funding",
  // "grants,
  // "global_goals",
  // "cooperation",
  // "partners",
  // "projects",
  "search",
  "sectors",
  "beneficiary_states",
]);

export function setFilters(scenario, period, params) {
  const filters = SCENARIOFILTERS[scenario];

  for (const name of filters) {
    let param = params[name] || null;
    if (param) {
      param = param.replace(/\+/g, " ");
    }

    if (
      name === "beneficiary" &&
      period === "2014-2021" &&
      param === "HU" &&
      !hungaryAllowedScenarios.has(scenario)
    )
      continue;

    FILTERS[name] = param;
  }
}

export default {
  data() {
    return {
      filters: FILTERS,
    };
  },

  watch: {
    // make sure every key exists from the start
    "filters.fm": "handleFilterFm",
    "filters.beneficiary": "handleFilterBeneficiary",
    "filters.region": "handleFilterRegion",
    "filters.sector": "handleFilterSector",
    "filters.sdg_no": "handleFilterSDG",
    "filters.area": "handleFilterArea",
    "filters.donor": "handleFilterDonor",
    "filters.DPP": "handleFilterDPP",
    "filters.thematic": "handleFilterThematic",
  },

  methods: {
    handleFilter(type, val, old) {
      // this should be handled by each component specifically
      //throw "Unhandled filter: " + type;
      //console.log(`» [${type}] filter:`, old,'→', val);
    },
    handleFilterFm(val, old) {
      const type = "fm";
      this.handleFilter(type, val, old);
    },
    handleFilterBeneficiary(val, old) {
      const type = "beneficiary";
      this.handleFilter(type, val, old);
    },
    handleFilterRegion(val, old) {
      const type = "region";
      this.handleFilter(type, val, old);
    },
    handleFilterSector(val, old) {
      const type = "sector";
      this.handleFilter(type, val, old);
    },
    handleFilterSDG(val, old) {
      const type = "sdg_no";
      this.handleFilter(type, val, old);
    },
    handleFilterArea(val, old) {
      const type = "area";
      this.handleFilter(type, val, old);
    },
    handleFilterDonor(val, old) {
      const type = "donor";
      this.handleFilter(type, val, old);
    },
    handleFilterDPP(val, old) {
      const type = "DPP";
      this.handleFilter(type, val, old);
    },
    handleFilterThematic(val, old) {
      const type = "thematic";
      this.handleFilter(type, val, old);
    },
  },
};
