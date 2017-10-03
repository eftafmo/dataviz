<template>
    <div :class="[$options.type, {embedded: embedded}]" v-show="hasData">
      <transition name="fade">
        <div class="allocation" :key="changed" v-if="data.project_percent_positive">
          <strong>{{ number(data.project_count) }} projects</strong>
            <template v-if="data.project_count_ended">
              <small>
                {{ data.project_percent_positive }}% of completed projects have had positive effects that are likely to continue beyond the funding period.
              </small>
            </template>
        </div>
        <div class="allocation" :key="changed" v-if="!data.project_percent_positive">
          <strong>No donor programme partners exist</strong>
        </div>
      </transition>
    </div>
</template>

<script>
import Summary from './Summary';
import ProjectsMixin from './mixins/Projects';


export default Summary.extend({
  mixins: [ProjectsMixin],

  computed: {
    data() {
      if (!this.hasData) return {}

      const out = this.aggregate(
        this.filtered,
        [],
        [
          'project_count',
          'project_count_positive',
          'project_count_ended',
        ],
        false
      );

      if (out.project_count_ended)
        out.project_percent_positive =  Math.round(
          out.project_count_positive / out.project_count_ended * 100
        );

      return out;
    },
  },
});
</script>
