/*
 * WARNING: this file is parsed in python.
 *          if you modify or rename it, make sure
 *          embedding code still works.
 */

import { default as Root } from "./components/Root";
import * as components from "./components";
import Sidebar from "./components/includes/Sidebar";
import { GlobalGoalsMap, GlobalGoalsMechanism } from "./components";

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
    thematic_bar_chart: components.ThematicBarChart,
    sectors: components.Sectors,
    xmap: components.GrantsMap,
    beneficiaries: components.Beneficiaries,
    sidebar: components.GrantsSidebar,
  },
};

export const Goals = {
  extends: _Base,
  name: "Goals",

  components: {
    mechanisms: components.GlobalGoalsMechanism,
    global_goals_chart: components.GlobalGoalsChart,
    xmap: components.GlobalGoalsMap,
    beneficiaries: components.Beneficiaries,
    sidebar: components.GoalsSidebar,
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
    thematic_bar_chart: components.ThematicBarChart,
    sectors: components.ProjectsSectors,
    xmap: components.ProjectsMap,
    beneficiaries: components.ProjectsBeneficiaries,
    sidebar: components.ProjectsSidebar,
    bilateral_initiatives_chart: components.BilateralInitiativesChart,
  },
};

export const Compare = {
  extends: _Base,
  name: "Compare",

  components: {
    compare_sectors_view: components.CompareSectorsView,
    compare_beneficiaries_view: components.CompareBeneficiariesView,

    funding_by_sector_chart: components.FundingBySectorChart,
    funding_by_period_chart: components.FundingByPeriodChart,
    beneficiaries: components.Beneficiaries,
  },
};

export const SearchRoot = {
  name: "SearchRoot",
  components: {
    sidebar_filters: Sidebar,
  },
};
