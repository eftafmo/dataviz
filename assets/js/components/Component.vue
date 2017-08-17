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

import ComponentMixin from './mixins/Component.js'


export default Base.extend({
  // set this on a derived component to build a "type tree".
  // useful for component class names.
  type: "viz",

  mixins: [ComponentMixin],

  props: {
    datasource: String,
  },

  computed: {
    classNames() {
      return this.$options.type;
    },

    embed_url() {
      const root = this.$root
      // it may be that this behaves like a primary component,
      // but is shallowly included into another.
      // we want the one that is first-level.
      let component = this
      while (component.$parent !== root)
        component = component.$parent

      const scenario = root.$options.name.toLowerCase(),
            tag = component.$vnode.componentOptions.tag,
            // hardcoding the base URL, because, oh well...
            path = `/embed/${scenario}/${tag}.js`;

      const url = new URL(path, window.location.href)

      for (const f in this.filters) {
        const v = this.filters[f]
        if (!v) continue
        url.searchParams.set(f, v)
      }

      return url.href
    },
  },
})


// concatenate the type values
Vue.config.optionMergeStrategies.type = function (previous, current) {
  if (!previous) return current
  if (!current) return previous

  return previous + " " + current
}
</script>
