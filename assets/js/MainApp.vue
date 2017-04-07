<template>
  <div id="app">
    <tag :dismissable="true" v-on:dismiss="dismiss">Domnul Gică Hagi</tag>
    Test output of {{ example.name }}.

    <sidebar-results></sidebar-results>
  </div>
</template>


<style>

</style>


<script>
//import ExampleComponent from './ExampleComponent.vue';
import Tag from './Tag.vue';
import SidebarResults from './SidebarResults.vue';

export default {
  name: 'app',
  components: {
    'tag': Tag,
    'sidebar-results': SidebarResults
  },
  data () {
    return {
      example: {
	      name: 'a test app',
      }
    }
  },
  methods: {
  dismiss: function() {
      console.log('MainAppEvent');
    }
  }
}
</script>
