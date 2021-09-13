<template>
  <div>
    <h1 class="page-title">Funding periods</h1>
    <div class="compare-beneficiaries-wrapper grant-dataviz">
      <funding-by-period-chart :initial="dataset" period="none" />
      <beneficiaries :initial="dataset" no-dropdown no-legend period="none">
        <template #title>
          <h2>Beneficiary States</h2>
        </template>
      </beneficiaries>
    </div>
  </div>
</template>

<script>
import Component from "../Component";
import Beneficiaries from "../Beneficiaries";
import WithCountries from "../mixins/WithCountries";
import DropdownFilter from "../includes/DropdownFilter";
import FundingByPeriodChart from "../FundingByPeriodChart";

export default {
  name: "CompareBeneficiariesView",
  components: { FundingByPeriodChart, Beneficiaries },
  extends: Component,
  mixins: [WithCountries],
};
</script>

<style scoped lang="less">
.compare-beneficiaries-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 2rem 5rem;
  margin: 3rem 0;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}
</style>