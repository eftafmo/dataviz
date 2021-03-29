<script>
import * as d3 from "d3";

import BaseNews from "./BaseNews";
import PartnersMixin from "./mixins/Partners";

export default BaseNews.extend({
  mixins: [PartnersMixin],

  methods: {
    /**
     * @param {Object} all_news
     * @returns {Object[]} news - all_news transformed in array, ordered by date
     */
    getSortedNews(all_news) {
      const news = d3.values(all_news);

      // sort by created date
      news.sort((a, b) => d3.descending(a.created, b.created));

      return news;
    },
  },
});
</script>
