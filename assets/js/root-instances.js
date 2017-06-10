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
    xmap: components.Map,
    beneficiaries: components.Beneficiaries,
    sidebar: components.Sidebar,
  },
});

export const Projects = Viz.extend({
  name: 'Projects',
  mixins: [BaseMixin],

  components: {
    mechanisms: components.Mechanisms,
    sectors: components.Sectors,
    xmap: components.Map,
    beneficiaries: components.Beneficiaries,
    sidebar: components.Sidebar,
  },
});

