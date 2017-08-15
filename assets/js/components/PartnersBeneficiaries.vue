<script>
import StatesBarChart from './StatesBarChart';

import PartnersMixin from './mixins/Partners';
import BeneficiariesBarChartMixin from './mixins/BeneficiariesBarChart';
import PartnersBarChartMixin from './mixins/PartnersBarChart';


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
          source: "PO",
          name: "Programme operators",
          type: Object,
        },
        projects: {
          source: "PJPT",
          name: "Project promoters",
          type: Object,
        },
      },

      title: 'Organisations with donor partner by beneficiary state'
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
