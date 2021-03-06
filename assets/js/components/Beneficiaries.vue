<script>
import * as d3 from 'd3';

import StatesBarChart from './StatesBarChart';

import BeneficiariesBarChartMixin from './mixins/BeneficiariesBarChart';
import WithFMsMixin from './mixins/WithFMs';


export default StatesBarChart.extend({
  mixins: [
    BeneficiariesBarChartMixin,
    WithFMsMixin,
  ],

  data() {
    return {
    }
  },

  created() {
    // aggregate by fms
    this.aggregate_by.push(
      {source: "fm", "destination": "fms", }
    )

    // don't filter by fm, because we need the total counts regardless
    // of filtering
    const fid = this.filter_by.indexOf("fm")
    if (fid !== -1) this.filter_by.splice(fid, 1)
  },

  computed: {
    legendClickFunc() {
      return this.toggleFm
    },

    legendFormatFunc() {
      return this.currency
    },

    types() {
      const out = {}

      for (const fmid in this.FMS) {
        const fm = this.FMS[fmid]
        out[fmid] = Object.assign({
          selected: this.isSelectedFm(fm),
          disabled: this.isDisabledFm(fm),
        }, fm)
      }

      return out
    },

    div_types() {
      return d3.values(this.FMS);
    },

    totals() {
      const state = this.filters[this.state_type]
      // we want to preserve the total even for disabled fms
      return this.data.reduce(
        (totals, item) => {
          // when filtering by state, ignore other states
          if (state && item.id != state) return totals
          for (const fmid in this.FMS) {
            const fm = this.FMS[fmid],
                  value = this.totalvaluefunc(item[fm.name]);
            let total = totals[fmid] || 0
            totals[fmid] = total + value
          }
          return totals
        }, {})
    },
  },

  methods: {
    _valuefunc(v) {
      // a slight detour for the logic below
      return v ? v.allocation : 0
    },
    valuefunc(item, fm) {
      fm = this.FMS[fm]
      return this.isDisabledFm(fm) ? 0 : this._valuefunc(item[fm.name])
    },
    totalvaluefunc(v) {
      return this._valuefunc(v)
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
