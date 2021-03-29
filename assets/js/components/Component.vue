<!--
     when deriving components from this, you should use
     :class="classNames" on the template's root element
-->

<style lang="less">
@duration: 0.5s;
@short_duration: 0.2s;

.fade-enter-active,
.fade-leave-active {
  transition: opacity @duration;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.fade-fast-enter-active,
.fade-fast-leave-active {
  transition: opacity @duration;
}

.fade-fast-enter,
.fade-fast-leave-to {
  opacity: 0;
}
</style>

<script>
import Vue from "vue";
import Base from "./Base";

import ComponentMixin from "./mixins/Component";

import { FILTERS } from "./mixins/WithFilters";

export default Base.extend({
  // set this on a derived component to build a "type tree".
  // useful for component class names.
  type: "viz",

  isDataviz: true,

  mixins: [ComponentMixin],

  props: {
    datasource: String,
    period: {
      type: String,
      default: "2009–2014",
    },
    embedded: {
      type: Boolean,
      default: false,
    },
    opts: {
      type: Object,
      default: () => {},
    },
  },

  beforeCreate() {
    // set filter values from opts.
    // do it before filters get bound, to avoid triggering handlers.
    const opts = this.$options.propsData.opts;

    for (const k in opts) {
      if (FILTERS[k] !== undefined) {
        FILTERS[k] = opts[k];
        delete opts[k];
      }
    }
  },

  computed: {
    classNames() {
      if (!this.isReady) return [];
      return this._getClassNames();
    },
  },

  methods: {
    _getClassNames() {
      const names = this.$options.type.split();
      if (this.embedded) names.push("embedded");

      return names;
    },
  },
});

// concatenate the type values
Vue.config.optionMergeStrategies.type = function (previous, current) {
  if (!previous) return current;
  if (!current) return previous;

  return previous + " " + current;
};
</script>
