<template>
    <ul class="news" v-if="hasData">
      <li v-for="news in data">
        <div class="content-item news_content">
        <a :href="`${news.link}`" target="_blank">
          <div class="body clearfix">
            <img :src="`${news.image}`">
            <h4 class="title">{{news.title}}</h4>
            <small>{{formatDate(news.created)}}</small>
          </div>
        </a>
        </div>
      </li>
    </ul>
</template>


<style lang="less">
.news {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
  }

  small {
    color: #898989;
  }

  img {
    float: left;
    width: 40%;
    margin-right: 1rem;
  }

  .title {
    font-size: 1.3rem;
  }

}
</style>


<script>
import * as d3 from 'd3';

import Component from './Component';


export default Component.extend({
  computed: {
    data() {
      const dataset = this.filtered;
      const unique = {};
      // use dict to remove duplicates
      for (const d of dataset) {
        for (const news of d.news){
          unique[news.link] = news;
        }
      }
      const out = [];
      for (const link in unique) {
        out.push(unique[link]);
      }
      // sort by date
      out.sort((a,b) => d3.descending(a.created,b.created));
      return out;
    },
  },

  methods: {
    formatDate(timestamp){
      const date = new Date(timestamp);
      let nav_lang;

      if (navigator.languages)
        nav_lang = navigator.languages[0];
      else
        nav_lang = "en"

      var options = { day: 'numeric', month: 'long', year: 'numeric' };
      var new_date = date.toLocaleDateString(nav_lang,options);
      return new_date
    },
  },
});
</script>
