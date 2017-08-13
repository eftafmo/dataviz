<template>
    <ul class="results" v-if="hasData">
       <li v-for="item in data" class="partner-result clearfix">
          <div class="partner-result-achievement"> {{ item.achievement }}{{ item.unit }}</div>
          <div class="partner-result"> {{ item.indicator }} </div>
       </li>
    </ul>
</template>


<style lang="less">
.results {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
  }

  small {
    color: #898989;
  }

  .partner-result {
    margin-bottom: .5rem;
    padding-left: .5rem;
  }

  .partner-result-achievement {
    display: inline;
    font-size: 2rem;
    color: black;
  }

  .partner-result {
    display: inline;
    font-size: 1.4rem;

  }

}
</style>


<script>
import * as d3 from 'd3';

import Component from './Component';
import PartnersMixin from './mixins/Partners';


export default Component.extend({
  mixins: [PartnersMixin],

  computed: {
    data() {
      const dataset = this.filtered;
      const aggregated = {
        DPP_programmes: d3.set(),
        dpp_projects: d3.set(),
        dpp_projects_ended: d3.set(),
        dpp_projects_coop: d3.set(),
        dpp_projects_improved: d3.set(),
      };

      for (const d of dataset) {
        for (let org_id in d.donor_programme_partners) {
          for (let prg of d.donor_programme_partners[org_id].programmes) {
            aggregated.DPP_programmes.add(prg);
          }
        }
        for (let prj in d.dpp_projects) {
          aggregated.dpp_projects.add(prj);
          const prj_data = d.dpp_projects[prj];
          if (prj_data.has_ended) {
            aggregated.dpp_projects_ended.add(prj);
          }
          if (prj_data.continued_coop) {
            aggregated.dpp_projects_coop.add(prj);
          }
          if (prj_data.improved_knowledge) {
            aggregated.dpp_projects_improved.add(prj);
          }
        }
      }
      const results = [];
      const num_DPP = aggregated.DPP_programmes.size();
      if (num_DPP > 0) {
        results.push(
          {
            achievement: num_DPP,
            indicator: this.singularize("programmes", num_DPP) + " with donor programme partners"
          }
        );
      }
      const num_dpp = aggregated.dpp_projects.size();
      if (num_dpp > 0) {
        results.push(
          { 
            achievement: num_dpp,
            indicator: this.singularize("projects", num_dpp) + " with donor project partners"
          }
        )
      }
      const num_prj_ended = aggregated.dpp_projects_ended.size();
      if (num_prj_ended) {
        results.push({
          achievement: Math.round(100 * aggregated.dpp_projects_coop.size() / num_prj_ended),
          unit: '%',
          indicator: "of partnership projects will continue the cooperation."
        });
        results.push({
          achievement: Math.round(100 * aggregated.dpp_projects_improved.size() / num_prj_ended),
          unit: '%',
          indicator: "of partnership projects have resulted in improved knowledge and mutual understanding between the partners."
        });
      }
      return results;
    },
  },

});
</script>