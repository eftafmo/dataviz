/*
 * WARNING: this file is parsed in python.
 *          if you modify or rename it, make sure
 *          embedding code still works.
 */

import * as components from "./components";
import { default as Root } from "./components/Root";

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
    xmap: components.GrantsMap,
    beneficiaries: components.Beneficiaries,
    xsummary: components.Summary,
    programmes: components.Programmes,
    results: components.Results,
    sidebar: components.GrantsSidebar,
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
    news: components.PartnersNews,
    programme_partners: components.PartnersDonorProgrammes,
    project_partners: components.PartnersDonorProjects,
    xsummary: components.PartnersSummary,
    results: components.PartnersResults,
    projects: components.PartnersProjects,
    sidebar: components.PartnersSidebar,
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
    news: components.ProjectsNews,
    projects: components.Projects,
    sidebar: components.ProjectsSidebar,
  },
});
