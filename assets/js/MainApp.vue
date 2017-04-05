<template>
<div id="app">
  Test output of {{ example.name }}.
</div>
</template>


<style>

</style>


<script>
//import ExampleComponent from './ExampleComponent.vue';

export default {
  name: 'app',
  components: {
    //ExampleComponent,
  },
  data () {
    return {
      example: {
	name: 'a test app',
      }
    }
  }
}
</script>
