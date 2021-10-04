<script>
import Beneficiaries from "./Beneficiaries";

export default {
  name: "CompareBeneficiariesChart",
  extends: Beneficiaries,
  methods: {
    preprocessItem(item) {
      // We need to display values for Greece from all periods combined.
      // So monkey patch this change, so the aggregation function combines
      // them automatically.
      if (item.beneficiary === "GR") {
        item.beneficiary = "EL";
        return { ...item };
      }
      return item;
    },
  },
};
</script>

<style scoped>

</style>