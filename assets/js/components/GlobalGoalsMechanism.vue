<script>
import Mechanisms from "./Mechanisms";

export default {
  name: "GlobalGoalsMechanism",
  extends: Mechanisms,
  data() {
    return {
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
};
</script>

<style scoped>

</style>