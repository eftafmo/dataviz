import Vue from 'vue';

import BaseMixin from './components/mixins/Base';
import * as components from './components/index';


const Base = Vue.extend({
  mixins: [BaseMixin],
  components: {
    globalfilters: components.GlobalFilters,
  },
});


export const Homepage = Base.extend({
  name: 'Homepage',

  components: {
    overview: components.Homepage,
    info: components.HomepageInfo,
  },
});


const Viz = Base.extend({
  components: {
    sidebar: components.Sidebar,
  },
});


export const Grants = Viz.extend({
  name: 'Grants',

  components: {
    mechanisms: components.Mechanisms,
    sectors: components.Sectors,
    xmap: components.AllocationMap,
    beneficiaries: components.Beneficiaries,
    overview: components.AllocationOverview,
    programmes: components.Programmes,
    results: components.Results,
  },
});

export const Projects = Viz.extend({
  name: 'Projects',

  components: {
    mechanisms: components.ProjectsMechanisms,
    sectors: components.ProjectsSectors,
    xmap: components.ProjectsMap,
    beneficiaries: components.ProjectsBeneficiaries,
    overview: components.ProjectsOverview,
    programmes: components.Programmes,
    news: components.News,
  },
});
