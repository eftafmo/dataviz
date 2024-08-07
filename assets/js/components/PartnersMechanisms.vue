<script>
import Component from "./Component";
import BaseMechanisms from "./Mechanisms";

import PartnersMixin from "./mixins/Partners";

export default {
  extends: BaseMechanisms,
  mixins: [PartnersMixin],
  data() {
    return {
      showTotals: false,
    };
  },
  computed: {
    aggregated() {
      const aggregated = this.aggregate(
        this.filtered,
        this.aggregate_by,
        this.aggregate_on,
      );
      for (const k in aggregated) {
        aggregated[k].allocation = 0;
      }
      const keys = new Set();
      const dataset = this.filtered;
      for (let d of dataset) {
        const key = d.programme + d.beneficiary + d.area;
        if (!keys.has(key)) {
          keys.add(key);
          aggregated[d.fm].allocation += d.allocation;
        }
      }
      return aggregated;
    },
  },
  created() {
    // allocation amounts are duplicated sometimes by donors,
    // so we need to overwrite it.
    this.aggregate_on = this.aggregate_on.filter(
      (item) => item !== "allocation",
    );
  },

  methods: {
    tooltipTemplate(ev, d) {
      return (
        `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <ul>
          <li>${d.programmes.size} partner ` +
        this.singularize(`programmes`, d.programmes.size) +
        `</li>
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
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
        `
      );
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.fms.is-partners {
  .legend {
    .fms {
      text-align: center;
    }
    .fm {
      border: none;
      padding-right: 0;
      margin-right: 0;
      min-width: initial;
      span.fill {
        vertical-align: middle;
        width: 1.4em;
        height: 1.4em;
        margin-right: 0.2em;
      }
    }
  }
}
</style>
