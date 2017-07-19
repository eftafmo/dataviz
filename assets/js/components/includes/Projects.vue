<template>
  <div class="projects">
    <div class="programme-item-header" @click="getProjects"> {{ name }} </div>
    <div v-if="posts.length != 0" class="programme-sublist-wrapper">
      <small class="programme-sublist-header">{{ sector }}</small>
      <ul class="programme-sublist">
        <li class="programme-sublist-item"
            v-for="value of posts.results">
             <span>{{ value.name }}</span>
         </li>
      </ul>
      <div v-if="posts.next" class="show-more small muted align-center">
         <button @click="showMore" type="button" class="btn-link">show 10 more results</button>
       </div>
    </div>
  </div>
</template>

<style lang="less">
.projects {
  .programme-sublist-wrapper {
    .show-more {
      button {
        &:before,&:after {
          content:' – '
        }
      }
    }
  }
.programme-sublist-item {
  list-style-type: inherit;
  span {
    color: #444;
  }
}

}
</style>

<script>
import Vue from 'vue';
import axios from 'axios';

export default Vue.extend({

  props: {
    id: String,
    country: String,
    sector: String,
    name: String
  },

 data() {
    return {
      posts: [],
      errors: [],
      }
    },

  methods: {
    getProjects() {
      const $this= this;
      if(this.posts.length == 0){
        axios.get(`/api/projects/?beneficiary=${$this.country}&programme=${$this.id}`)
          .then(response => {
            this.posts = response.data
          })
          .catch(e => {
            this.errors.push(e)
          });
      }
      else
        this.posts=[]
    },
    showMore() {
      let href = this.posts.next;
      if(href){
        axios.get(""+href+"")
          .then(response => {
            this.posts.next = response.data.next
            this.posts.count = response.data.count
            this.posts.previous = response.data.previous
            this.posts.results.push.apply(this.posts.results, response.data.results)
          })
          .catch(e => {
            this.errors.push(e)
        });
      }
    }

  },

});

</script>
