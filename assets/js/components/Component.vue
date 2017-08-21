<style lang="less">
@duration: .5s;
@short_duration: .2s;

.fade-enter-active, .fade-leave-active {
  transition: opacity @duration;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.fade-fast-enter-active, .fade-fast-leave-active {
  transition: opacity @duration;
}

.fade-fast-enter, .fade-fast-leave-to {
  opacity: 0;
}

</style>


<script>
import Vue from 'vue'
import Base from './Base'

import ComponentMixin from './mixins/Component'

import {FILTERS} from '../globals';


export default Base.extend({
  // set this on a derived component to build a "type tree".
  // useful for component class names.
  type: "viz",

  isDataviz: true,

  mixins: [ComponentMixin],

  props: {
    datasource: String,
    embedded: {
      type: Boolean,
      default: false,
    },
    opts: {
      type: Object,
      default: () => {},
    },
  },

  computed: {
    classNames() {
      return this.$options.type // + embedded ? " embedded" : ""
    },
  },

  beforeCreate() {
    // set filter values from opts.
    // do it before filters get bound, to avoid triggering handlers.
    const opts = this.$options.propsData.opts

    for (const k in opts) {
      if (FILTERS[k] !== undefined) {
        FILTERS[k] = opts[k]
        delete opts[k]
      }
    }
  },
})


// concatenate the type values
Vue.config.optionMergeStrategies.type = function (previous, current) {
  if (!previous) return current
  if (!current) return previous

  return previous + " " + current
}
</script>
