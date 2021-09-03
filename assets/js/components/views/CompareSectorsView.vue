<template>
  <div>
    <h1 class="page-title">
      <span>Funding by sectors in</span>
      <dropdown-filter
        filter="beneficiary"
        title="all Beneficiary States"
        :items="BENEFICIARY_ARRAY"
        class="viz-select-heading"
      />
    </h1>
    <div class="compare-sector-wrapper grant-dataviz">
      <funding-by-sector-chart
        v-for="period in periodsToCompare"
        :key="period"
        :initial="dataset"
        :period="period"
      ></funding-by-sector-chart>
    </div>
  </div>
</template>

<script>
import FundingBySectorChart from "../FundingBySectorChart";
import Component from "../Component";
import DropdownFilter from "../includes/DropdownFilter";
import WithCountries from "../mixins/WithCountries";

export default {
  name: "CompareSectorsView",
  components: { DropdownFilter, FundingBySectorChart },
  extends: Component,
  mixins: [WithCountries],
  data() {
    return {
      periodsToCompare: ["2009-2014", "2014-2021"],
    };
  },
};
</script>

<style scoped lang="less">
.compare-sector-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 2rem 5rem;
  margin: 3rem 0;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}
</style>