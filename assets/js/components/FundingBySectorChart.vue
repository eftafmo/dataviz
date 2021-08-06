<template>
  <div :class="classNames" class="funding-by-sector-chart">
    <embeddor :period="period" tag="sectors" />
    <div>
      <span>Funding by sectors in</span>
      <dropdown-filter
        filter="beneficiary"
        title="all Beneficiary States"
        :items="BENEFICIARY_ARRAY"
        class="viz-select-heading"
      />
    </div>
    <pre>
      {{ data }}
    </pre>
    <chart-container :width="width" :height="height">
      <svg :viewBox="`0 0 ${width} ${height}`">
        <g class="chart"></g>
      </svg>
    </chart-container>
  </div>
</template>

<script>
import Chart from "./Chart";
import WithCountriesMixin from "./mixins/WithCountries";
import Embeddor from "./includes/Embeddor";
import DropdownFilter from "./includes/DropdownFilter";
import WithSectors from "./mixins/WithSectors";
import { slugify } from "../lib/util";

export default {
  name: "FundingBySectorChart",
  components: { DropdownFilter, Embeddor },
  extends: Chart,
  type: "overview",

  mixins: [WithCountriesMixin, WithSectors],
  data() {
    return {
      aggregate_by: ["sector"],
      filter_by: ["beneficiary"],
      width: 500,
      height: 500,
    };
  },
  computed: {
    data() {
      return Object.values(this.aggregated).map((item) => {
        return {
          sector: this.SECTORS[slugify(item.sector)],
          allocation: item.net_allocation,
        };
      });
    },
  },
  methods: {
    renderChart() {},
  },
};
</script>

<style scoped lang="less">
.funding-by-sector-chart {
  padding: 2rem 0;
}
</style>