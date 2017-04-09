<template>
  <div class="sidebar-tab-pane" 
       v-bind:class="{ 
        'is-selected': selected,
        'is-loading': loading
       }">
    <ul class="sidebar-tab-result-list" v-if="results">
      <li v-for="result in results">
        <a class="sidebar-result-news" :href="result.url" target="_blank">
          <img class="thumbnail" :src="result.thumbnailURL" alt="Thumbnail">
          <div class="body">
            <h4 class="title">{{ result.title }}</h4>
            <time>{{ result.publishDate }}</time>
          </div>
        </a>
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
            title: 'Funding lifeline for greek asylum service',
            publishDate: '24 February 2016',
            thumbnailURL: '',
            url: '#'
          },

          {
            title: 'Bringing ancient history to light: a crosscultural treasure hunt',
            publishDate: '12 January 2016',
            thumbnailURL: '',
            url: '#'
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
