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
};
</script>

<style scoped>

</style>