<script>
import Mechanisms from "./Mechanisms";

export default {
  name: "GlobalGoalsMechanism",
  extends: Mechanisms,
  data() {
    return {
      showTotals: false,
      allocationType: "net",
      aggregate_on: [
        "allocation",
        "net_allocation",
        {
          source: "beneficiary",
          destination: "beneficiaries",
          type: String,
          exclude: "is_ta",
        },
        {
          source: "sectors",
          destination: "sectors",
          type: Array,
          exclude: "is_ta",
        },
        {
          source: "areas",
          destination: "areas",
          type: Array,
          exclude: "is_ta",
        },
        { source: "programmes", type: Object },
      ],
    };
  },
  methods: {
    tooltipTemplate(ev, d) {
      return (
        `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <div class="subtitle-container">
          <span class="donor-states">${d.donor_list}</span>
        </div>
        <ul>
          <li>${this.getBeneficiaryCount(d.beneficiaries)} ` +
        this.singularize(
          `Beneficiary States`,
          this.getBeneficiaryCount(d.beneficiaries),
        ) +
        `</li>
          <li>${d.sectors.size} ` +
        this.singularize(`sectors`, d.sectors.size) +
        `</li>
          <li>${d.areas.size} ` +
        this.singularize(`programme areas`, d.areas.size) +
        `</li>
          <li>${d.programmes.size}  ` +
        (d.programmes.size == 1
          ? "programme/agreement"
          : "programmes and agreements") +
        `</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
        `
      );
    },
  },
};
</script>

<style scoped>

</style>
