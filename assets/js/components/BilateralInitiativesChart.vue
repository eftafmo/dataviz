<script>
import StatesBarChart from "./StatesBarChart";
import BeneficiariesBarChartMixin from "./mixins/BeneficiariesBarChart";
import WithFMsMixin from "./mixins/WithFMs";

export default {
  name: "BilateralInitiativesChart",
  extends: StatesBarChart,
  mixins: [BeneficiariesBarChartMixin, WithFMsMixin],

  data() {
    return {
      hideIfEmpty: true,
      aggregate_by: ["beneficiary"],
      aggregate_on: ["allocation", "count"],
    };
  },

  computed: {
    legendFormatFunc() {
      return this.currency;
    },

    types() {
      return {
        allocation: {
          id: "allocation",
          name: "Bilateral Initiatives",
          color: "#e98300",
          pattern: "#ba6800",
          stripesFill: "url(#stripes-pattern-allocation)",
        },
      };
    },
    div_types() {
      return Object.values(this.types);
    },
  },
  methods: {
    _valuefunc(v) {
      return v?.allocation || 0;
    },
    valuefunc(item) {
      return this._valuefunc(item);
    },
    totalvaluefunc(v) {
      return this._valuefunc(v);
    },

    tooltipTemplate(ev, d) {
      const value = this.valuefunc(d);

      return `
        <div class="title-container">
          <img src="${this.get_flag(d.id)}" alt=""/>
          <span class="name">${d.name}</span>
        </div>
        <ul>
          <li>
            ${this.currency(value)} contracted
          </li>
          <li>
            ${d.count} ${this.singularize("Bilateral Initiatives", d.count)}
          </li>
        </ul>
        <span class="action">Click to filter by Beneficiary State</span>
      `;
    },
  },
};
</script>

<style scoped>

</style>
