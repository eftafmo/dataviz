<template>
  <span class="tag">
    <slot></slot>
    <span class="icon icon-close" v-if="dismissable" v-on:click="dismiss"></span>
  </span>
</template>

<style>
  .tag {
    display: inline-block;
    padding: .3334em .6667em;
    background: #50B9FF;
    color: #000;
    vertical-align: middle;
  }
  .tag .icon {
    opacity: .6;
  }
</style>

<script>
  import Vue from 'vue';

/*
   even if this is imported only for side effects externally,
   it still needs a default export or vue won't be able to inject
   its default render function (using the local template)
*/
  export default Vue.component('tag', {
    props: {
      dismissable: {
        type: Boolean,
        default: false
      }
    },
    methods: {
      dismiss: function(event) {
        this.$emit('dismiss');
        // console.log('this', this);
        // console.log('event', event);
        // alert('dismiss tag');
      }
    }
  })
</script>
