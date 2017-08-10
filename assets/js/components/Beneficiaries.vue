<script>
import * as d3 from 'd3';

import StatesBarChart from './StatesBarChart';

import BeneficiariesMixin from './mixins/BeneficiariesBarChart';
import WithFMsMixin from './mixins/WithFMs';


export default StatesBarChart.extend({
  mixins: [
    BeneficiariesMixin,
    WithFMsMixin,
  ],

  data() {
    return {
      title: 'Funding across beneficiary states',
    }
  },

  created() {
    // aggregate by fms, but only at the final level
    this.aggregate_by.push(
      {source: "fm", "destination": "fms", }//final: true}
    )
  },

  computed: {
    div_types() {
      return d3.values(this.FMS);
    },
  },

  methods: {
    valuefunc(item, fm) {
      fm = this.FMS[fm].name
      return item[fm] ? item[fm].allocation : 0
    },

    tooltipTemplate(d) {
      // TODO: this is getting beyond silly.
      const data = d.data
                    .filter( (x) => x.value != 0 );
      const datatxt = data
        .map( (x) => `
            <li>${ x.name } : ${ this.currency(x.value) }</li>
        ` )
        .join("");

      return `
        <div class="title-container">
        <svg>
          <use xlink:href="#${this.get_flag_name(d.id)}" />
        </svg>
          <span class="name">${d.name}</span>
        </div>
        <ul>${ datatxt }</ul>
        <span class="action">Click to filter by beneficiary state</span>
      `;
    },
  },
});
</script>
