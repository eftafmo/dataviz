import Vue from 'vue';

import BaseMixin from './components/mixins/Base';
import * as components from './components/index';


const Base = Vue.extend({
  mixins: [BaseMixin],
});


export const Homepage = Base.extend({
  name: 'Homepage',

  components: {
    overview: components.Overview,
    info: components.HomepageInfo,
    globalfilters: components.GlobalFilters,

  },
});


const Viz = Base.extend({
  // TODO: do we want the filter bar on all pages?7
  components: {
    globalfilters: components.GlobalFilters,
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
    sidebar: components.Sidebar,
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
    sidebar: components.Sidebar,
  },
});
