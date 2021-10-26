<script>
import BarChart from "./BarChart";

export default {
  name: "GlobalGoalsBarChart",
  extends: BarChart,
  data() {
    return {
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
      let programmeSize = `
          <li>
            ${d.programmes.size}
            ${this.singularize("programmes", d.programmes.size)}
          </li> `;
      if (d.sdg_no === 16 || d.sdg_no === 17) {
        programmeSize = `
            <li>${d.programmes.size}
            ${
              d.programmes.size === 1
                ? "programme/agreement"
                : "programmes and agreements"
            }
            </li>`;
      }
      return `
        <div class="title-container">
          <span>${d.name}</span>
        </div>
        <ul>
          <li>
            ${this.currency(d.allocation)}
            ${this.allocationType} allocation
          </li>
          <li>
            ${this.getBeneficiaryCount(d.beneficiaries)}
            ${this.singularize(
              "Beneficiary States",
              this.getBeneficiaryCount(d.beneficiaries)
            )}
          </li>
          <li>
            ${d.sectors.size}
            ${this.singularize("sectors", d.sectors.size)}
          </li>
          <li>
            ${d.areas.size}
            ${this.singularize("programme areas", d.areas.size)}
          </li>
          ${programmeSize}
        </ul>
      `;
    },
  },
};
</script>

<style scoped>

</style>
