/*
 * WARNING: this file is parsed in python.
 *          if you modify or rename it, make sure
 *          embedding code still works.
 */

import {default as Root} from './components/Root';
import * as components from './components';


const Base = Root.extend({
  components: {
    globalfilters: components.GlobalFilters,
  },
});


export const Index = Base.extend({
  name: "Index",

  components: {
    overview: components.Overview,
  },
});


export const Grants = Base.extend({
  name: "Grants",

  components: {
    mechanisms: components.Mechanisms,
    sectors: components.Sectors,
    xmap: components.AllocationMap,
    beneficiaries: components.Beneficiaries,
    xsummary: components.Summary,
    programmes: components.Programmes,
    results: components.Results,
  },
});

export const Partners = Base.extend({
  name: "Partners",

  components: {
    mechanisms: components.PartnersMechanisms,
    sectors: components.PartnersSectors,
    xmap: components.PartnersMap,
    donors: components.PartnersDonors,
    beneficiaries: components.PartnersBeneficiaries,
    news: components.PartnerNews,
    programme_partners: components.PartnersDonorProgrammes,
    project_partners: components.PartnersDonorProjects,
    xsummary: components.PartnersSummary,
    results: components.PartnersResults,
  },
});

export const Projects = Base.extend({
  name: "Projects",

  components: {
    mechanisms: components.ProjectsMechanisms,
    sectors: components.ProjectsSectors,
    xmap: components.ProjectsMap,
    beneficiaries: components.ProjectsBeneficiaries,
    xsummary: components.ProjectsSummary,
    programmes: components.Programmes,
    news: components.News,
    projects: components.Projects,
  },
});

export const Search = Base.extend({
  name: "Search",
});
