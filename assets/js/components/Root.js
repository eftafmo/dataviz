import Vue from 'vue';
import debounce from 'lodash.debounce';
import BaseMixin from './mixins/Base';
import {FILTERS} from '../globals';


function getURL(obj) {
  // obj must have a .href property.
  // it also shouldn't be mutated by anything else.
  let url = obj._url;
  if (url === undefined)
    url = obj._url = new URL(obj.href, window.location.href);

  return url;
}


export default Vue.extend({
  mixins: [BaseMixin],

  beforeCreate() {
    // set filters from querystring.
    // do it before filters get bound, to avoid triggering handlers.
    const params = getURL(window.location).searchParams;

    for (const name in FILTERS) {
      FILTERS[name] = params.get(name) || null;
    }
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
        this._updateURL(url);

        a.href = url.href;
      }
    },

    _updateURL(url) {
      const params = url.searchParams;

      for (const name in this.filters) {
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
      this._updateURL(location);

      // TODO: what's the more appropriate UX, push or replace?
      history.replaceState(null, null, location.href);

      this.updateAnchors();
    },
  },
});
