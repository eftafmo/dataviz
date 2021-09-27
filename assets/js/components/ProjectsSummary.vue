<template>
  <div v-show="hasData" :class="classNames">
    <transition name="fade">
      <div v-if="data.project_count" :key="changed" class="allocation">
        <strong>{{ number(data.project_count) }} projects</strong>
        <template v-if="data.project_count_ended">
          <small>
            {{ data.project_percent_positive }}% of completed projects have had
            positive effects that are likely to continue beyond the funding
            period.
          </small>
        </template>
        <template v-if="!data.project_count_ended">
          <small>
            Not enough data about projects with positive effects that are likely
            to continue beyond the funding period.
          </small>
        </template>
      </div>
    </transition>
  </div>
</template>


<script>
import Summary from "./Summary";
import ProjectsMixin from "./mixins/Projects";

export default {
  extends: Summary,
  mixins: [ProjectsMixin],

  computed: {
    data() {
      if (!this.hasData) return {};
      // hand-made aggregation of project counts, to accomodate breakdown by programme and nuts
      const dataset = this.filtered;
      const projects = new Set();
      const projects_ended = new Set();
      const projects_positive = new Set();

      for (let d of dataset) {
        for (let prg in d.programmes) {
          for (let nut in d.programmes[prg].nuts) {
            if (
              this.filters.region &&
              nut.substr(0, this.filters.region.length) !== this.filters.region
            ) {
              continue;
            }
            const item = d.programmes[prg].nuts[nut];

            (item.total || []).forEach((i) => projects.add(i));
            (item.ended || []).forEach((i) => projects_ended.add(i));
            (item.positive || []).forEach((i) => projects_positive.add(i));
          }
        }
      }

      const out = {
        project_count: projects.size,
        project_count_ended: projects_ended.size,
        project_count_positive: projects_positive.size,
      };
      if (out.project_count_ended)
        out.project_percent_positive = Math.round(
          (out.project_count_positive / out.project_count_ended) * 100
        );

      return out;
    },
  },
};
</script>
