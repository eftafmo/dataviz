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
    }
  },

  created() {
    // programmes, PO and PJPT are already in aggregate_on
    this.aggregate_on = this.aggregate_on.filter(item => item.source !== 'programme' && item.source !== 'programmes');
    this.aggregate_on.push({source: 'programme', destination: 'DPP_programmes', type: String, exclude_empty: 'DPP'});
    this.aggregate_on.push({source: 'DPP', destination: 'DPP', type: String});
    this.aggregate_on.push({source: 'PJDPP', destination: 'PJDPP', type: Object});
    this.aggregate_on.push({source: 'projects', destination: 'projects', type: Object});
  },


  methods: {
    tooltipTemplate(d) {
      let datatxt = '';
      const num_PO = d.PO === undefined ? 0 : d.PO.size();
      const num_DPP = d.DPP === undefined ? 0 : d.DPP.size();
      // size instead of size() is not a bug. Maybe should replace all d3.set() with Set ?
      const num_prg_DPP = d.DPP_programmes === undefined ? 0 : d.DPP_programmes.size();

      const num_PJPT = d.PJPT === undefined ? 0 : d.PJPT.size();
      const num_dpp = d.PJDPP === undefined ? 0 : d.PJDPP.size();
      const num_prj_dpp = d.projects === undefined ? 0 : d.projects.size();

      if ( num_PO ) {
        datatxt += `<li>${num_PO} programme ` +
          this.singularize('operators', num_PO) + ` working with ${num_DPP} donor ` +
          this.singularize('partners', num_DPP) + ` in ${num_prg_DPP} ` +
          this.singularize('programmes', num_prg_DPP);
      }
      if ( num_PJPT ) {
        datatxt +=  `<li>${num_PJPT} project ` +
          this.singularize('promoters', num_PJPT) + ` working with ${num_dpp} donor ` +
          this.singularize('partners', num_dpp) + ` in ${num_prj_dpp} ` +
          this.singularize('projects', num_prj_dpp);
      }
      return `
        <div class="title-container">
          <svg>
            <use xlink:href="#${this.get_flag_name(d.id)}" />
          </svg>
          <span class="name">${d.name}</span>
        </div>
        <ul>${datatxt}</ul>
        <span class="action">Click to filter by ${ this.state_type } state</span>`;
    },
  }
});
</script>
