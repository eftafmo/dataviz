<template>
  <ul :class="classNames">
    <li v-for="news in data" :key="news.link" class="content-item">
      <a class="news-content" :href="`${news.link}`" target="_blank">
        <img :src="`${news.image}`" />
        <div :class="{ no_img: !news.image }">
          <h4 class="title">{{ news.title }}</h4>
          <small>{{ formatDate(news.created) }}</small>
        </div>
      </a>
    </li>
  </ul>
</template>


<script>
import Component from "./Component";

export default {
  extends: Component,
  type: "news",

  computed: {
    data() {
      if (!this.hasData) return [];

      const dataset = this.filtered;
      const unique = {};

      // use dict to remove duplicates
      for (const d of dataset) {
        for (const news of d.news) {
          unique[news.link] = news;
        }
      }

      const out = this.getSortedNews(unique);

      return out;
    },
  },

  methods: {
    formatDate(timestamp) {
      const date = new Date(timestamp);
      let nav_lang;

      if (navigator.languages) nav_lang = navigator.languages[0];
      else nav_lang = "en";

      var options = { day: "numeric", month: "long", year: "numeric" };
      var new_date = date.toLocaleDateString(nav_lang, options);
      return new_date;
    },
  },
};
</script>

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

  .news-content {
    display: flex;
    text-decoration: none;
  }

  img {
    margin-right: 1rem;
  }

  .title {
    font-size: 1.3rem;
  }
}
</style>

