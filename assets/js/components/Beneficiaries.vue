<template>
<div class="beneficiaries-viz">
  <div v-if="hasData" class="legend">
    <fm-legend :fms="fms" class="clearfix">
      <template slot="fm-content" scope="x">
        <span :style="{backgroundColor: x.fm.colour}"></span>
        {{ x.fm.name }}
      </template>
    </fm-legend>
  </div>
  <svg :width="width" :height="height">
    <g class="chart">
      <g class="domain" :transform="`translate(${reserved},0)`">
        <line :y2="height" />
      </g>
    </g>
  </svg>
</div>
</template>


<style lang="less">
.beneficiaries-viz {
  .legend .fm span {
    width: 10px; height: 10px;
    display: inline-block;
  }
  .legend li {
    list-style-type: none;
    display: inline-block;
    margin-right: 2rem;
  }
  .legend .fm {
    transition: all .5s ease;
  }
  .legend .fm.disabled {
    filter: grayscale(100%);
    opacity: 0.5;
  }

  .legend .fm.selected {
    text-shadow: 0 0 1px #999;
  }

  svg .domain line {
    stroke: #ccc;
    shape-rendering: crispEdges;
  }

  .chart {
    .beneficiary {
      text {
        font-size: 10px;
        font-family: sans-serif;
        fill: #333;
        text-anchor: end;
      }
    }
  }
}

</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import CSVReadingMixin from './mixins/CSVReading';
import WithFMsMixin from './mixins/WithFMs';
// this one's mostly loaded for side-effects
import {get_flag_name} from './mixins/WithCountries';


export default Vue.extend({
  mixins: [
    BaseMixin, CSVReadingMixin,
    ChartMixin, WithFMsMixin,
  ],

  props: {
    width: Number,
    minHeight: {
      type: Number,
      default: 0,
    },
    itemHeight: {
      type: Number,
      default: 20,
    },
    reserved: {
      // reserved for country labels. TODO: change this name
      type: Number,
      default: 120,
    },
  },

  data() {
    return {
      height: this.minHeight,
    };
  },

  computed: {
    data() {
      // massage data so it's appropriate for a stacked barchart

      const keys = this.filters.fm ?
                   [this.filters.fm] :
                   this.dataset.columns.slice(2); // skips id & name
      const stack = d3.stack()
                      .keys(keys);

      // transpose because we want items grouped by row.
      // (d3.stack returns items grouped by columns (keys))
      const data = d3.transpose(stack(this.dataset));

      // add some useful properties
      data.forEach( (row, i) => {
        Object.assign(row, {
          id: this.dataset[i].id,
          country: this.dataset[i].name,
          total: d3.sum(row, (d) => d[1] - d[0]),
        });

        row.forEach( (item, j) => {
          // the fm, per-item
          item.fm = keys[j];
          // it will be useful to know the country at this level too
          item.country = row.country;
          // also clear old data
          delete item.data;
        })
      });

      // sort by total
      data.sort((a, b) => b.total - a.total);

      // and return filtered
      return data.filter((d) => d.total != 0);
    },

    x() {
      return d3.scaleLinear()
               .range([0, this.width - this.reserved])
               .domain([0, d3.max(this.data, (d) => d.total)]);
    },

    y() {
      return d3.scaleBand()
               .paddingInner(0.5) // TODO: propify
               .align(1)  // TODO: propify
               .rangeRound([0, this.height])
               .domain(this.data.map( (d) => d.country ));
    },
  },

  methods: {
    renderItems(context) {
      // this could receive both a selection and a transition
      const selection = context.selection ? context.selection() : context;

      const items = selection.selectAll("rect.fm").data(
        (d) => d, // re-bind local data (to create a join)
        (d) => [d.country, d.fm] // the key
      );

      items.enter().append("rect") // ENTER-only
        .attr("class", (d) => "fm " + d.fm)
        .attr("fill", (d) => this.colour(d.fm))
        .attr("y", 0) // this is handled in the parent
        .attr("height", this.y.bandwidth)

      .merge(items) // ENTER + UPDATE
        .attr("x", (d) => this.x(d[0]))
        .attr("width", (d) => this.x(d[1]) - this.x(d[0]));

      items.exit() // EXIT
        .remove();
    },

    renderChart() {
      const data = this.data;

      // resize the chart to fit the data
      this.height = Math.max(this.minHeight, // TODO: lose min-height?
                             this.itemHeight * data.length);

      const chart = this.chart;

      /*
       * main stuff
       */
      const beneficiaries = chart
	    .selectAll("g.beneficiary")
            .data(data, (d) => d.country); /* JOIN */

      beneficiaries.exit() /* EXIT */
        .remove();

      // insert the rows instead of appending
      // (makes sure the domain line stays on top)
      const bentered = beneficiaries.enter().insert("g") /* ENTER */
        .attr("class", (d) => "beneficiary " + d.country);

      const bmerged = bentered.merge(beneficiaries) /* ENTER _and_ UPDATE */
        .attr("transform", (d) => `translate(0,${this.y(d.country)})`);

      /*
       * render the "legend" part
       */
      // (it's not really a legend 'cause it's part of the row. you get it.)
      const _padding = 5,
            // this could be smarter, but whatever
            __flg = { // the image dimensions
              w: 60,
              h: 40,
            },
            _flag = { // our dimensions
              w: __flg.w * this.y.bandwidth() / __flg.h,
              h: this.y.bandwidth(),
            }

      const country = bentered.append("g")
            .attr("transform",
                  `translate(${this.reserved - (_padding + _flag.w)},0)`
                 );

      country.append("text")
        .text((d) => d.country)
        .attr("x", -_padding)
      // v-align
        .attr("y", this.y.bandwidth() * this.y.paddingInner())
        .attr("dy", ".32em"); // magical self-centering offset

      country.append("use")
        .attr("xlink:href", (d) => `#${get_flag_name(d.country)}`)
        .attr("width", _flag.w)
        .attr("height", _flag.h);

      /*
       * render data items
       */
      const items = bentered.append("g")
            .attr("class", "items")
            .attr("transform", (d) => `translate(${this.reserved},0)`);

      // but we want to run the item rendering both in ENTER and UPDATE
      items.merge(beneficiaries.select("g.items"))
        .call(this.renderItems);
    },

    handleFilterFm() {
      this.render();
    },
  },
});

</script>
