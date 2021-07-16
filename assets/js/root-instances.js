/*
 * WARNING: this file is parsed in python.
 *          if you modify or rename it, make sure
 *          embedding code still works.
 */

import { default as Root } from "./components/Root";
import * as components from "./components";

const _Base = {
  extends: Root,

  components: {
    globalfilters: components.GlobalFilters,
  },
};

export const Index = {
  extends: _Base,
  name: "Index",

  components: {
    overview: components.Overview,
    overview_funding: components.OverviewFunding,
  },
};

export const Grants = {
  extends: _Base,
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
};

export const Partners = {
  extends: _Base,
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
};

export const Projects = {
  extends: _Base,
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
};
