<template>
  <div class="sidebar-tab-pane" 
       v-bind:class="{ 
        'is-selected': selected,
        'is-loading': loading
       }">
    <ul class="no-list"
        v-if="results">
      <li v-for="result in results">
        <h4>{{ result.title }}</h4>
        <p>{{ result.description }}</p>
      </li>
    </ul>

    <div class="small muted align-center">
      &ndash;
      <button type="button" class="btn-link">show 10 more results</button>
      |
      <a href="#search" class="muted">show all</a>
      &ndash;
    </div>

  </div>    
</template>

<style>
  
</style>

<script>
  
  import Vue from 'vue';

  var SidebarResultTab = Vue.component('sidebar-result-tab', {

    props: {
      selected: {
        type: Boolean,
        default: false
      }
    },

    watch: {
      selected () { this.loadResults(); }
    },

    data () {
      return {
        loading: false,
        results: [
          {
            title: 'First result title',
            description: 'First result description'
          },

          {
            title: 'Second result title',
            description: 'Second result description'
          }
        ]
      }
    },

    methods: {

      loadResults() {
        var self = this;
        self.loading = true;

        window.setTimeout(function() {
          // simulate ajax call
          self.loading = false;
        }, 1000);
      }

    }

  });

  export default SidebarResultTab;

</script>
