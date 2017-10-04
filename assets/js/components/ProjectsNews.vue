<script>
import * as d3 from 'd3';
import orderBy from 'lodash.orderby';
import BaseNews from './BaseNews';
import ProjectsMixin from './mixins/Projects';

export default BaseNews.extend({

  mixins: [
    ProjectsMixin,
  ],
  methods: {
    /**
     * @param {Object} all_news
     * @returns {Object[]} news - news for specific region (nuts), ordered by relevance
     */
    getSortedNews(all_news) {
      const deep_search = true;
      const news_for_nuts = this.getNewsForRegion(all_news, this.localfilters.region || "", deep_search);
      // sometimes this.localfilters.region is null (for filtering by country or removing filters)
      if(this.localfilters.region) {
        // sort by relevance and created date
        orderBy(news_for_nuts, ["nuts", "created"], ["desc", "desc"])
      } else {
        // sort by created date
        news_for_nuts.sort((a,b) => d3.descending(a.created,b.created));
      }

      return news_for_nuts;
    },
    /**
     * recursive function that returns news for a region
     * @param {Object} all_news
     * @param {string|null} region - will find news for region, for null, it will return all news
     * @param {boolean} deep_search - find news for included areas, only the first time, to avoid duplicating news
     * @returns {Object[]} filtered_news - news for specific region (nuts), ordered by relevance, looks for parent region news if
     * news for region is less than 3 ex: for RO31, return RO31, RO311, RO312, if results are less than 3, return RO3, or RO, 
     * it will not return from neighbor regions like RO32
     */
    getNewsForRegion(all_news, region, deep_search) {
      let filtered_news = [];

      for (const link in all_news) {
        const nuts = all_news[link].nuts;
        if(deep_search) {
          // if region is "RO12" it will include nuts like "RO12" and "RO121"
          if(nuts.substr(0, region.length) === region || region === "") {
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
      // search for parent news if region news are less than 3, stop at country code ex: "RO"
      if(filtered_news.length <= 3 && region.length >= 2) {
        filtered_news = [...filtered_news, ...this.getNewsForRegion(all_news, region.substr(0, region.length-1, deep_search))];
      }
      return filtered_news;
    },
  }

});
</script>
