<template>
    <div :class="classNames">
       <dl v-for="item in data" class="partner-result clearfix">
          <dt class="partner-result-achievement">{{ number(item.achievement) }}{{ item.unit }}</dt>
          <dd class="partner-result">{{ item.indicator }} </dd>
       </dl>
    </div>
</template>


<style lang="less">
.dataviz .viz.results {
  dl dt {
      font-weight: bold;
      display: inline;
      text-align: center;
      border-left: 3px solid rgb(0, 117, 188);
      padding-left: 1rem;
      font-size: 1.6rem;
  }

  dl dd {
    margin:2px 0;
    font-size: 1.4rem;
    display: inline;
  }

  small {
    color: #898989;
  }
}
</style>


<script>
import * as d3 from 'd3';

import Component from './Component';
import PartnersMixin from './mixins/Partners';


export default {
  extends: Component,
  type: "results",

  mixins: [
    PartnersMixin,
  ],

  computed: {
    data() {
      if (!this.hasData) return []

      const dataset = this.filtered;
      const aggregated = {
        DPP_programmes: d3.set(),
        dpp_programmes: d3.set(),
        dpp_projects: d3.set(),
        dpp_projects_ended: d3.set(),
        dpp_projects_coop: d3.set(),
        dpp_projects_improved: d3.set(),
      };

      for (const d of dataset) {
        if (d.DPP) {
          aggregated.DPP_programmes.add(d.programme);
        }
        if (d.PJDPP) {
          aggregated.dpp_programmes.add(d.programme);
        }
        for (let prj in d.projects) {
          aggregated.dpp_projects.add(prj);
          const prj_data = d.projects[prj];
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
      const num_prg_dpp = aggregated.dpp_programmes.size();
      if (num_prg_dpp > 0) {
        results.push(
          {
            achievement: num_prg_dpp,
            indicator: this.singularize("programmes", num_prg_dpp) + " with donor project partners"
          }
        );
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

  methods: {
    format(v) {
      return this.number(v)
    },
  },

}
</script>
