import debounce from 'lodash.debounce';

import Base from './Base';

import Embeddor from './includes/Embeddor'

// access filters directly before they get bound, to avoid triggering handlers
import {FILTERS, SCENARIOFILTERS} from './mixins/WithFilters'


function getURL(obj) {
  // obj must have a .href property.
  // it also shouldn't be mutated by anything else.
  let url = obj._url;
  if (url === undefined)
    url = obj._url = new URL(obj.href, window.location.href);

  return url;
}

function getScenario(url) {
  const match = url.pathname.match(/^\/(\w+)?\/?$/)
  if (!match) return null

  const scenario = match[1]
  if (scenario === undefined) return "index"
  // test if this is a known scenario
  if (SCENARIOFILTERS[scenario] === undefined) return null
  return scenario
}


export default {
  extends: Base,

  components: {
    embeddor: Embeddor,
  },

  data() {
    return {
      datasource: null,
      vizcomponents: [],
    };
  },

  beforeCreate() {
    // set filters from querystring.
    const url = getURL(window.location),
          params = url.searchParams,
          scenario = getScenario(url)
    const filters = SCENARIOFILTERS[scenario]
    for (const name of filters) {
      let param = params.get(name) || null
      if (param) {
        param = param.replace(/\+/g, ' ')
      }
      FILTERS[name] = param
    }

    this.scenario = scenario
  },

  created() {
    // don't rely on the backend to serve updated anchors
    this.updateAnchors();
  },

  mounted() {
    /** !!! WARNING, TODO !!! **/
    return;

    const vizcomps = []
    // recurse through all children to find those that are dataviz
    let parent = this

    const recurse = (current) => {
      for (const comp of current.$children) {
        if (comp.$options.isDataviz)
          vizcomps.push(comp) // end of the road
        else
          recurse(comp) // not end of the road
      }
    }

    recurse(this)

    this.vizcomponents = vizcomps
  },


  methods: {
    updateAnchors() {
      // we can run this async
      let updater = this._debouncedUpdateAnchors;
      if (updater === undefined)
        updater = this._debouncedUpdateAnchors = debounce(
          this._updateAnchors, 100
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
        const scenario = getScenario(url)
        if (!scenario) continue

        this._updateURL(url, SCENARIOFILTERS[scenario])

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
        if (value)
          params.set(name, value);
      }
    },

    handleFilter(type, val, old) {
      const location = getURL(window.location);
      this._updateURL(location, SCENARIOFILTERS[this.scenario]);

      history.replaceState(null, null, location.href);

      this.updateAnchors();
    },
  },
}
