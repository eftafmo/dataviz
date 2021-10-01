// for use with StatesBarChart components

export default {
  type: "beneficiaries",

  data() {
    return {
      state_type: "beneficiary",
    };
  },

  computed: {
    STATES() {
      return this.BENEFICIARIES;
    },

    clickFunc() {
      return this.toggleBeneficiary;
    },
  },

  methods: {
    handleFilterBeneficiary() {
      this.handleStateFilter();
    },
  },
};
