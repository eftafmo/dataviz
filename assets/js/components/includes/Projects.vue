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
  .programme-item-header {
    position: relative;
    color: #444;
    padding-left: 2rem;
    display: block;
    cursor: pointer;
    &:hover {
      text-decoration: underline;
    }
  }

  .programme-item-header.active {
    color: #005494;
    border-top: 1px solid #ddd;
    padding-top: 1rem;
  }
  .active.programme-item-header{
      &:before {
          transform: rotate(90deg);
      }
  }

  .programme-sublist-header {
    margin-left: 2rem;
  }

  .programme-item-header:before {
    content: "\25BA";
    margin-right: .5rem;
    transition: all 300ms;
    left: 4px;
    font-size: 1.1rem;
    position: absolute;
  }

  .programme-sublist {
      margin-left: 3.5rem;
  }

  .spinning:after {
    content: '';
    position: absolute;
    top: -11px;
    height: 37px;
    width: 37px;
    background: url(/assets/imgs/spinner.svg);
    right: -20px;
    transform: scale(0.6);
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
      let target = this.$el.querySelector('.programme-item-header')
      target.classList.add('spinning')

      if(this.posts.length == 0){
        axios.get(`/api/projects/?beneficiary=${$this.country}&programme=${$this.id}`)
          .then(response => {
            this.posts = response.data
            if(target.classList.contains('spinning'))
              target.classList.remove('spinning')
          })
          .catch(e => {
            this.errors.push(e)
          });
      }
      else
        if(target.classList.contains('spinning'))
              target.classList.remove('spinning')
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
