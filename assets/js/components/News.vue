<template>
    <ul class="news" v-if="hasData">
      <li v-for="d in data">
        <div class="content-item news_content">
        <a :href="`${d.link}`">
          <div class="body clearfix">
            <img :src="`${d.image}`">
            <h4 class="title">{{d.title}}</h4>
            <small>{{moment(d.created)}}</small>
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

  .indicator {
    border-left: 3px solid red;
    margin-bottom: .5rem;
    padding-left: .5rem;
  }

  .indicator-achievement {
    display: inline;
    font-size: 2rem;
    color: black;
  }

  .indicator-name {
    display: inline;
    font-size: 1.2rem;

  }

}
</style>

<script>

import Vue from 'vue';
import * as d3 from 'd3';
import BaseMixin from './mixins/Base';
import WithSectorsMixin from './mixins/WithSectors';
import {FILTERS} from '../globals.js'
import moment from 'moment';

export default Vue.extend({
  mixins: [
    BaseMixin, WithSectorsMixin,
  ],

  computed: {
    data() {
    const dataset = this.dataset;
    return dataset;
    },
  },

  methods: {
  moment(date){
    return moment(date).format('Do MMMM YYYY ');
  }
}


});

</script>
