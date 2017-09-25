// site-wide navigation filters
export const FILTERS = {
  fm: null,
  beneficiary: null,
  sector: null,
  area: null,
  donor: null,
  DPP: null,
}


export default {
  data() {
    return {
      filters: FILTERS,
    }
  },

  watch: {
    // make sure every key exists from the start
    'filters.fm': 'handleFilterFm',
    'filters.beneficiary': 'handleFilterBeneficiary',
    'filters.sector': 'handleFilterSector',
    'filters.area': 'handleFilterArea',
    'filters.donor': 'handleFilterDonor',
    'filters.DPP': 'handleFilterDPP',
  },

  methods: {
    handleFilter(type, val, old) {
      // this should be handled by each component specifically
      return
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
    handleFilterSector(val, old) {
      const type = "sector";
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
  },
}
