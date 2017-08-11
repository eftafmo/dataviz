<script>
import StatesBarChart from './StatesBarChart';

import PartnersMixin from './mixins/Partners';
import BeneficiariesBarChartMixin from './mixins/BeneficiariesBarChart';
import PartnersBarChartMixin from './mixins/PartnersBarChart.js';


export default StatesBarChart.extend({
  mixins: [
    PartnersMixin,
    BeneficiariesBarChartMixin,
    PartnersBarChartMixin,
  ],

  data() {
    return {
      columns: {
        programmes: {
          source: "programme_operators",
          label: "Programme organisations",
        },
        projects: {
          source: "project_promoters",
          label: "Project organisations",
        },
      },

      title: 'Organizations with donor partner by beneficiary state'
    }
  },

  updated() {
    let dropdown = this.$el.querySelector('.viz-select');
    let title = this.$el.querySelector('h2')
    if(!dropdown) return;
    dropdown.style.cssFloat = 'initial'
    dropdown.style.marginBottom = '2rem'
    title.style.marginBottom = '1rem'
  },
});
</script>
