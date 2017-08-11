<script>
import StatesBarChart from './StatesBarChart';

import PartnersMixin from './mixins/Partners';
import PartnersBarChartMixin from './mixins/PartnersBarChart';


export default StatesBarChart.extend({
  type: "donors",

  mixins: [
    PartnersMixin,
    PartnersBarChartMixin,
  ],

  data() {
    return {
      state_type: "donor",

      columns: {
        programmes: {
          source: "donor_programme_partners",
          name: "Donor programme partners",
        },
        projects: {
          source: "donor_project_partners",
          name: "Donor project partners",
        },
      },

      title: 'Organisations by donor state'
    }
  },

  computed: {
    STATES() {
      return this.DONORS
    },

    longestText() {
      return this.longestDonor
    },

    clickFunc() {
      return this.toggleDonor
    },
  },

  methods: {
    handleFilterDonor() {
      this.handleStateFilter()
    },
  }
});
</script>
