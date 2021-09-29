<template>
  <bar-chart
    main-filter="sdg_no"
    embed-tag="global_goals_chart"
    title="Sustainable Development Goals"
    drop-down-title="Sustainable Development Goals"
    :all-items="sdgArray"
    show-id
    hide-zero
  >
    <template #before-chart>
      <transition name="fade">
        <div v-if="currentGoal && currentGoalImage" class="current-goal">
          <img :src="currentGoalImage" :alt="currentGoal.name" />
        </div>
      </transition>
    </template>
  </bar-chart>
</template>

<script>
import sdgArray from "@js/constants/sdg.json5";
import BarChart from "./BarChart";
import { getAssetUrl } from "../lib/util";
import WithFiltersMixin from "./mixins/WithFilters";

export default {
  name: "GlobalGoalsChart",
  components: { BarChart },
  mixins: [WithFiltersMixin],
  type: "",

  data() {
    return {
      sdgArray,
    };
  },
  computed: {
    currentGoal() {
      return (
        this.filters.sdg_no &&
        sdgArray.find(
          (item) => item.id.toString() === this.filters.sdg_no.toString()
        )
      );
    },
    currentGoalImage() {
      return (
        this.currentGoal && getAssetUrl(`imgs/goals/${this.currentGoal.icon}`)
      );
    },
  },
};
</script>

<style lang="less">
.current-goal {
  width: 19rem;
  height: 19rem;
  margin: 0 auto 2rem auto;
  padding: 1rem;

  img {
    max-width: 100%;
    max-height: 100%;
  }
}
</style>