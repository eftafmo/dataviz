import Vue from 'vue';

import BaseMixin from './components/mixins/Base';
import ProjectsMixin from './components/mixins/Projects';
import * as components from './components/index';
import {Tabs, Tab} from 'vue-tabs-component';


const Base = Vue.extend({
  mixins: [BaseMixin],
});


export const Homepage = Base.extend({
  name: 'Homepage',

  components: {
    overview: components.Overview,
  },
});


const Viz = Base.extend({
  // TODO: do we want the filter bar on all pages?
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
    allocation_overview: components.Allocation_overview,
    programmes: components.Programmes,
    results: components.Results,
    tabs: Tabs,
    tab: Tab,
  },
});

export const Projects = Viz.extend({
  name: 'Projects',

  components: {
    mechanisms: components.Mechanisms,
    sectors: components.Sectors.extend({
      mixins: [ProjectsMixin],
    }),
    xmap: components.ProjectsMap,
    beneficiaries: components.Beneficiaries,
    allocation_overview: components.Allocation_overview,
  },
});
