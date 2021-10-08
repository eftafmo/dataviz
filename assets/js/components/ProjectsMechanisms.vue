<script>
import Mechanisms from "./Mechanisms";
import ProjectsMixin from "./mixins/Projects";

export default {
  extends: Mechanisms,
  mixins: [ProjectsMixin],

  data() {
    return {};
  },

  methods: {
    tooltipTemplate(ev, d) {
      // TODO: this is silly. turn this into a component.
      return (
        `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <div class="subtitle-container">
          <span class="donor-states">${d.donor_list}</span>
        </div>
        <ul>
          <li>${this.number(d.projects.size)} projects</li>
          <li>${this.currency(d.allocation)}</li>
          <li>${this.getBeneficiaryCount(d.beneficiaries)} ` +
        this.singularize(
          `Beneficiary States`,
          this.getBeneficiaryCount(d.beneficiaries)
        ) +
        `</li>
          <li>${d.sectors.size} ` +
        this.singularize(`sectors`, d.sectors.size) +
        `</li>
          <li>${d.areas.size} ` +
        this.singularize(`programme areas`, d.areas.size) +
        `</li>
          <li>${d.programmes.size}  ` +
        this.singularize(`programmes`, d.programmes.size) +
        `</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
      `
      );
    },
  },
};
</script>
