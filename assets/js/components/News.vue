<template>
    <ul class="news" v-if="hasData">
      <li v-for="news in data">
        <div class="content-item news_content">
        <a :href="`${news.link}`">
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

import Vue from 'vue';
import * as d3 from 'd3';
import BaseMixin from './mixins/Base';
import WithSectorsMixin from './mixins/WithSectors';
import {FILTERS} from '../globals.js'


export default Vue.extend({
  mixins: [
    BaseMixin, WithSectorsMixin,
  ],

  computed: {
    data() {
    const dataset = this.filter(this.dataset);
    const out = [];
    for (let d of dataset) {
      for (let news in d.news){
        out.push(d.news[news])
      }
    }
    out.sort((a,b) => d3.descending(a.created,b.created));
    return out;
    },
  },

  methods: {
  formatDate(date){
    date = new Date;
    var options = { day: 'numeric', month: 'long', year: 'numeric' };
    var new_date = date.toLocaleDateString('en',options);
    return new_date
  }
}


});

</script>
