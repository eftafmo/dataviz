<template>
    <ul :class="classNames">
      <li class="content-item news_content" v-for="news in data">
        <a class="body clearfix" :href="`${news.link}`" target="_blank">
          <img :src="`${news.image}`">
          <div :class="{ no_img : !news.image }" class="pull-right news_text">
            <h4 class="title">{{news.title}}</h4>
            <small>{{formatDate(news.created)}}</small>
          </div>
        </a>
      </li>
    </ul>
</template>


<style lang="less">
.dataviz .viz.news {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
  }

  small {
    color: #898989;
  }

  .pull-right {
    float: right;
  }

  .news_text {
    width: calc(~'60% - 1rem');
    &.no_img {
      float: initial;
      width: 100%;
    }
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
import Component from './Component';


export default Component.extend({
  type: "news",

  computed: {
    data() {
      if (!this.hasData) return []

      const dataset = this.filtered;
      const unique = {};

      // use dict to remove duplicates
      for (const d of dataset) {
        for (const news of d.news){
          unique[news.link] = news;
        }
      }

      const out = this.getSortedNews(unique);

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
