<style lang="less">
@duration: .5s;

.fade-enter-active, .fade-leave-active {
  transition: opacity @duration;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>


<script>
import Base from './Base';


export default {
  extends: Base,

  props: {
    datasource: String,
  },
};
</script>
