import debounce from "lodash.debounce";

import Base from "./Base";

// access filters directly before they get bound, to avoid triggering handlers
import { FILTERS, SCENARIOFILTERS, setFilters } from "./mixins/WithFilters";

function getURL(obj) {
  // obj must have a .href property.
  // it also shouldn't be mutated by anything else.
  let url = obj._url;
  if (url === undefined)
    url = obj._url = new URL(obj.href, window.location.href);

  return url;
}

const _scenario_url = new RegExp(
  "^/(\\d{4}-\\d{4}|compare)/(\\w+)?(/|.html)?$",
);

function getScenario(url) {
  const match = url.pathname.match(_scenario_url);
  if (!match) return {};

  const period = match[1];
  let scenario = match[2];
  if (scenario === undefined) scenario = "index";
  // test if this is a known scenario
  if (SCENARIOFILTERS[scenario] === undefined) return {};

  return { period, scenario };
}

export default {
  extends: Base,
  props: {
    datasource: String,
  },
  beforeCreate() {
    // set filters from querystring.
    const url = getURL(window.location);
    const { period, scenario } = getScenario(url);
    const params = Object.fromEntries(url.searchParams.entries());

    setFilters(
      scenario,
      period,
      Object.fromEntries(url.searchParams.entries()),
    );

    this.scenario = scenario;
  },
  created() {
    // don't rely on the backend to serve updated anchors
    this.updateAnchors();
  },
  methods: {
    updateAnchors() {
      // we can run this async
      let updater = this._debouncedUpdateAnchors;
      if (updater === undefined)
        updater = this._debouncedUpdateAnchors = debounce(
          this._updateAnchors,
          100,
        );

      updater();
    },
    _updateAnchors() {
      const location = getURL(window.location);

      const anchors = document.getElementsByTagName("a");
      for (const a of anchors) {
        if (!a.href) continue;

        const url = getURL(a);
        if (url.origin !== location.origin) continue;
        const { period, scenario } = getScenario(url);
        if (!scenario) continue;

        this._updateURL(url, SCENARIOFILTERS[scenario]);

        a.href = url.href;
      }
    },
    _updateURL(url, filters) {
      const params = url.searchParams;

      for (const name of filters) {
        const value = this.filters[name];

        // remove the param and add it back if necessary
        // (so we have a nice, predictable order. not OCD at all.)
        params.delete(name);
        if (value) params.set(name, value);
      }
    },
    handleFilter(type, val, old) {
      const location = getURL(window.location);
      this._updateURL(location, SCENARIOFILTERS[this.scenario]);

      history.replaceState(null, null, location.href);

      this.updateAnchors();
    },
  },
};
