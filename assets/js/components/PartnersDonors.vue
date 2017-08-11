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

  created() {
    // need to re-remove donors from filters, because it's re-added
    // by PartnersMixin. silly.
    const col = "donor"
    const idx = this.filter_by.indexOf(col)
    if (idx !== -1)
      this.filter_by.splice(idx, 1)
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
