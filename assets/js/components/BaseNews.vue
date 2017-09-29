<template>
    <ul class="news">
      <li v-for="news in data">
        <div class="content-item news_content">
        <a :href="`${news.link}`" target="_blank">
          <div class="body clearfix">
            <img :src="`${news.image}`">
            <h4 class="title">{{news.title}}</h4>
            <h4 class="title">{{news.nuts}}</h4>
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
      if (!this.hasData) return []

      const dataset = this.filtered;
      const unique = {};

      // use dict to remove duplicates
      for (const d of dataset) {
        for (const news of d.news){
          unique[news.link] = news;
        }
      }

      const out = this.getSortedNewsForNUTS(unique) || [];

      return out;
    },
  },

  methods: {
    /**
     * @param {Object} all_news
     * @returns {Object[]} news - news for specific region (nuts), ordered by relevance
     */
    getSortedNewsForNUTS(all_news) {
      const deep_search = true;
      const news_for_nuts = this.getNewsForRegion(all_news, this.localfilters.region || "", deep_search);

      // sometimes this.localfilters.region is null (for filtering by country or removing filters)
      if(this.localfilters.region) {
        // sort by relevance and created date
        news_for_nuts.sort(this.compareNewsRelevance);
      } else {
        // sort by created date
        news_for_nuts.sort((a,b) => d3.descending(a.created,b.created));
      }

      return news_for_nuts;
    },
    /**
     * @param {Object} all_news
     * @param {string|null} region - will find news for region, for null, it will return all news
     * @param {boolean} deep_search - find news for included areas, only the first time, to avoid duplicating news
     * @returns {Object[]} filtered_news - news for specific region (nuts), ordered by relevance, looks for parent region news if
     * news for region is less than 3
     */
    getNewsForRegion(all_news, region, deep_search) {
      let filtered_news = [];

      for (const link in all_news) {
        const nuts = all_news[link].nuts;
        if(deep_search) {
          // if region is "RO12" it will include nuts like "RO12" and "RO121"
          if(nuts.substr(0, region.length) === region || !region) {
            filtered_news.push(all_news[link]);
          }
        } else {
          // if region is "RO12" it will only take nuts = "RO12"
          if(nuts === region || !region) {
            filtered_news.push(all_news[link]);
          }
        }
      }
      deep_search = false;
      // search for parent news if region new is less than 3, stop ar country code ex: "RO"
      if(filtered_news.length <= 3 && region.length >= 2) {
        filtered_news = [...filtered_news, ...this.getNewsForRegion(all_news, region.substr(0, region.length-1, deep_search))];
      }
      return filtered_news;
    },
    /**
     * will order descending by nuts value (ex: "RO121" > "RO12"), if nuts is equal, it will order by created date
     * @param {Object} a
     * @param {Object} b
     * @returns {number} 1 or -1
     */
    compareNewsRelevance(a, b) {
      if (a.nuts < b.nuts) {
        return 1;
      }
      if (a.nuts > b.nuts) {
        return -1;
      } else if (a.nuts == b.nuts) {
        if (a.created >= b.created) {
          return -1;
        } else {
          return 1;
        }
      }
    },
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
