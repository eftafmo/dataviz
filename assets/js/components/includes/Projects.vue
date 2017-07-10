<template>
  <div v-if="nodes" class="programme-sublist-wrapper">
    <small class="programme-sublist-header">{{ sector }}</small>
    <ul class="programme-sublist">
      <li class="programme-sublist-item"
          v-for="value of data.results">
           {{ value.name }}
       </li>
    </ul>
    <div v-if="posts.next" class="show-more small muted align-center">
       &ndash;
       <button @click="showMore()" type="button" class="btn-link">show 10 more results</button>
      &ndash;
     </div>
  </div>
</template>

<style lang="less">

</style>

<script>
import Vue from 'vue';
import axios from 'axios';

export default Vue.extend({

  props: {
    id: String,
    country: String,
    doajax: Array,
    sector: String,
  },

 data() {
    return {
      posts: [],
      errors: [],
      done: false,
      nodes: false
      }
    },

  computed : {
    data() {
      return this.posts
    },
  },

  methods: {
    showNodes() {
       if(this.country == this.doajax[0] && this.id == this.doajax[1] && this.done == false) {
        this.nodes = true
        return true
       }
    },

    getProjects() {
      const $this= this;
      if(this.showNodes()) {
        axios.get(`/api/projects/?beneficiary=${$this.country}&programme=${$this.id}`)
          .then(response => {
            this.posts = response.data
            this.done = true;
          })
          .catch(e => {
            this.errors.push(e)
          });
      }
      else {
        this.nodes = false;
        this.done = false;
      }
    },

    showMore(){
      let href = this.posts.next;
      if(href){
        axios.get(""+href+"")
          .then(response => {
            this.posts.next = response.data.next
            this.posts.count = response.data.count
            this.posts.previous = response.data.previous
            this.posts.results = this.posts.results.concat(response.data.results)
          })
          .catch(e => {
            this.errors.push(e)
        });
      }
    }

  },

   watch: {
    'doajax': 'getProjects',
  }
});

</script>
