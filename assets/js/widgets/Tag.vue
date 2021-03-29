<template>
  <span class="tag">
    <slot></slot>
    <span
      class="icon icon-close"
      v-if="dismissable"
      v-on:click="dismiss"
    ></span>
  </span>
</template>

<style>
.tag {
  display: inline-block;
  padding: 0.3334em 0.6667em;
  background: #50b9ff;
  color: #000;
  vertical-align: middle;
}
.tag .icon {
  opacity: 0.6;
}
</style>

<script>
export default {
  props: {
    dismissable: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    dismiss: function (event) {
      this.$emit("dismiss");
      // console.log('this', this);
      // console.log('event', event);
      // alert('dismiss tag');
    },
  },
};
</script>
