<template>
    <div :class="classNames" v-show="hasData">
      <transition name="fade">
        <div class="allocation" :key="changed" v-if="data.project_count">
          <strong>{{ number(data.project_count) }} projects</strong>
            <template v-if="data.project_count_ended">
              <small>
                {{ data.project_percent_positive }}% of completed projects have had positive effects that are likely to continue beyond the funding period.
              </small>
            </template>
            <template v-if="!data.project_count_ended">
              <small>
                Not enough data about projects with positive effects that are likely to continue beyond the funding period.
              </small>
            </template>
        </div>
      </transition>
    </div>
</template>


<script>
import Summary from './Summary';
import ProjectsMixin from './mixins/Projects';


export default {
  extends: Summary,
  mixins: [
    ProjectsMixin,
  ],

  computed: {
    data() {
      if (!this.hasData) return {}
      // hand-made aggregation of project counts, to accomodate breakdown by programme and nuts
      const dataset = this.filtered;
      const out = {
        project_count: 0,
        project_count_ended: 0,
        project_count_positive: 0,
      }

      for (let d of dataset) {
        for (let prg in d.programmes) {
          for (let nut in d.programmes[prg].nuts) {
            if (this.filters.region && nut.substr(0, this.filters.region.length) !== this.filters.region) {
              continue;
            }
            const item = d.programmes[prg].nuts[nut];
            out.project_count += item.count;
            out.project_count_ended += item.ended;
            out.project_count_positive += item.positive;
          }
        }
      }

      if (out.project_count_ended)
        out.project_percent_positive =  Math.round(
          out.project_count_positive / out.project_count_ended * 100
        );

      return out;
    },
  },
}
</script>
