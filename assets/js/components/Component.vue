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
import Vue from 'vue';
import Base from './Base';


export default Base.extend({
  // set this on a derived component to build a "type tree".
  // useful for component class names.
  type: "viz",

  props: {
    datasource: String,
  },

  computed: {
    classNames() {
      return this.$options.type;
    },
  },
});


// concatenate the type values
Vue.config.optionMergeStrategies.type = function (previous, current) {
  if (!previous) return current
  if (!current) return previous

  return previous + " " + current
}

</script>
