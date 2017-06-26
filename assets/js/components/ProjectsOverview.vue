<template>
    <div  v-if="hasData" class="sidebar-header">
      <transition name="fade">
        <div class="allocation" :key="transitioned">
          <strong>{{ number(data.project_count) }} projects</strong>
          <small>
            {{ number(data.project_count_ended) }} projects completed<template v-if="data.project_count_positive">, of which {{ data.project_percent_positive }}% have had positive effects that are likely to continue beyond the funding period.</template>
          </small>
        </div>
      </transition>
    </div>
</template>

<script>
import AllocationOverview from './AllocationOverview';
import ProjectsMixin from './mixins/Projects';


export default AllocationOverview.extend({
  mixins: [ProjectsMixin],

  computed: {
    data() {
      const dataset = this.filter(this.dataset);
      const out = this.aggregate(
        dataset,
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
