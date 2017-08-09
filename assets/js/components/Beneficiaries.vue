<script>
import StatesBarChart from './StatesBarChart';

import WithFMsMixin from './mixins/WithFMs';


export default StatesBarChart.extend({
  type: "beneficiaries",

  mixins: [
    WithFMsMixin,
  ],

  data() {
    return {
      state_type: "beneficiary",
      div_type: "fm",

      title: 'Funding across beneficiary states',
    }
  },

  computed: {
    STATES() {
      return this.BENEFICIARIES
    },

    longestText() {
      return this.longestBeneficiary
    },

    clickFunc() {
      return this.toggleBeneficiary
    }
  },

  methods: {
    tooltipTemplate(d) {
      // TODO: this is getting beyond silly.
      const data = d.data
                    .filter( (x) => x.allocation != 0 );
      const datatxt = data
        .map( (x) => `
            <li>${ x.name } : ${ this.currency(x.allocation) }</li>
        ` )
        .join("");

      return `
        <div class="title-container">
        <svg>
          <use xlink:href="#${this.get_flag_name(d.id)}" />
        </svg>
          <span class="name">${d.name}</span>
        </div>
        <ul> ${ datatxt } </ul>
        <span class="action">Click to filter by beneficiary state</span>
      `;
    },

    handleFilterBeneficiary() {
      this.handleStateFilter()
    },
  },
});
</script>
