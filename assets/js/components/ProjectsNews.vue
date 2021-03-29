<script>
import orderBy from "lodash.orderby";
import BaseNews from "./BaseNews";
import ProjectsMixin from "./mixins/Projects";
import WithRegionsMixin from "./mixins/WithRegions";

export default BaseNews.extend({
  mixins: [ProjectsMixin, WithRegionsMixin],
  methods: {
    /**
     * @param {Object} all_news
     * @returns {Object[]} news - news for specific region (nuts), ordered by relevance
     */
    getSortedNews(all_news) {
      const deep_search = true;
      // sometimes this.filters.region is null (filtering by country or removing filters)
      const news_for_nuts = this.getSortedNewsForRegion(
        all_news,
        this.filters.region || "",
        deep_search
      );

      return news_for_nuts;
    },
    /**
     * recursive function that returns sorted news for a region
     * @param {Object} all_news
     * @param {string|null} region - will find news for region, for null, it will return all news
     * @param {boolean} deep_search - find news for included areas, only the first time, to avoid duplicating news
     * @returns {Object[]} filtered_news - news for specific region (nuts), ordered by relevance, ex for RO31:
     * - looks for sub-regions news ex: RO31x, RO31 included, everything sorted desc by created
     * - looks for parent region news ex: RO3(if exists), RO, everything sorted desc by created
     * - it will not return from neighbour regions like RO32, RO32x
     */
    getSortedNewsForRegion(all_news, region, deep_search) {
      let filtered_news = [];

      for (const link in all_news) {
        const nuts = all_news[link].nuts;
        if (deep_search) {
          // if region is "RO31" it will include "RO31" and "RO31x"
          if (region === "" || this.isAncestorRegion(region, nuts)) {
            filtered_news.push(all_news[link]);
          }
        } else {
          // if region is "RO31" it will only take nuts = "RO31"
          if (nuts === region || !region) {
            filtered_news.push(all_news[link]);
          }
        }
      }
      deep_search = false;
      filtered_news = orderBy(filtered_news, ["created"], ["desc"]);
      // search for parent news if region news are less than 3, stop at country code ex: "RO"
      if (region.length >= 2) {
        filtered_news = [
          ...filtered_news,
          ...this.getSortedNewsForRegion(
            all_news,
            region.substr(0, region.length - 1, deep_search)
          ),
        ];
      }

      return filtered_news;
    },
  },
});
</script>
