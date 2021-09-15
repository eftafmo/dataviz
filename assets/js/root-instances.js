/*
 * WARNING: this file is parsed in python.
 *          if you modify or rename it, make sure
 *          embedding code still works.
 */

import { default as Root } from "./components/Root";
import * as components from "./components";
import Sidebar from "./components/includes/Sidebar";

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
    overview_results: components.OverviewResults,
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
    sidebar: components.GrantsSidebar,
  },
};

export const GlobalGoals = {
  extends: _Base,
  name: "GlobalGoals",

  components: {
    mechanisms: components.Mechanisms,
    global_goals_chart: components.GlobalGoalsChart,
    sectors: components.Sectors,
    xmap: components.GrantsMap,
    beneficiaries: components.Beneficiaries,
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
    programme_partners: components.PartnersDonorProgrammes,
    project_partners: components.PartnersDonorProjects,
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
    sidebar: components.ProjectsSidebar,
  },
};

export const CompareSectors = {
  extends: _Base,
  name: "CompareSectors",

  components: {
    compare_sectors_view: components.CompareSectorsView,
    funding_by_sector_chart: components.FundingBySectorChart,
  },
};

export const CompareBeneficiaries = {
  extends: _Base,
  name: "CompareBeneficiaries",

  components: {
    compare_beneficiaries_view: components.CompareBeneficiariesView,
    funding_by_period_chart: components.FundingByPeriodChart,
  },
};

export const SearchRoot = {
  name: "SearchRoot",
  components: {
    sidebar_filters: Sidebar,
  },
};
