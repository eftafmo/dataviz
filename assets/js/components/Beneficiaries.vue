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
  <div v-if="hasData" class="dropdown">
    <dropdown :filter="filter" :title="title" :items="data"></dropdown>
  </div>
  <svg :width="width" :height="height">
    <g class="chart">
      <g class="domain" :transform="`translate(${reserved},0)`">
        <line />
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
      cursor: pointer;
      pointer-events: all;

      ._fill {
        fill: none;
      }

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
import WithCountriesMixin, {get_flag_name} from './mixins/WithCountries';
import Dropdown from './includes/DropdownFilter.vue';

export default Vue.extend({
  mixins: [
    BaseMixin, CSVReadingMixin,
    ChartMixin, WithFMsMixin, WithCountriesMixin
  ],

  components: {
    'dropdown': Dropdown,
  },

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
      xheight: 0,
      height: this.minHeight,
    };
  },

  computed: {

    title(){
      var title = "Select a beneficiary state"
      return title
    },
    filter(){
       var filter = "region"
       return filter
    },
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

      // iterate to add some useful properties
      data.forEach( (row, i) => {
        // these will be removed
        const _zeroes = [];

        row.forEach( (item, j) => {
          const value = item[1] - item[0];
          if (value == 0) {
            _zeroes.push(j);
          }
          item.value = value;

          // the fm, per-item
          item.fm = keys[j];

          // also clear old data
          delete item.data;
        });

        if(_zeroes) {
          _zeroes.reverse();
          _zeroes.forEach((i) => row.splice(i, 1));
        }

        Object.assign(row, {
          id: this.dataset[i].id,
          name: this.dataset[i].name,
          total: d3.sum(row, (d) => d.value),
        });
      });

      // sort by total
      data.sort((a, b) => b.total - a.total);

      // return filtered
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
               .align(0.5)  // TODO: propify
               .rangeRound([0, this.xheight])
               .domain(this.data.map( (d) => d.id ));
    },
  },

  methods: {
    renderItems(context) {
      // this could receive both a selection and a transition
      const selection = context.selection ? context.selection() : context,
            t = context;

      const items = selection.selectAll("rect.fm").data(
        (d) => d, // re-bind local data (to create a join)
        (d) => d.fm // the key
      );

      items.enter().append("rect") // ENTER-only
        .attr("class", (d) => "fm " + d.fm)
        .attr("fill", (d) => this.colour(d.fm))
        .attr("y", 0) // this is handled in the parent
        .attr("height", this.y.bandwidth)

      .merge(items) // ENTER + UPDATE
        .transition(t)
        .attr("x", (d) => this.x(d[0]))
        .attr("width", (d) => this.x(d[1]) - this.x(d[0]));

      items.exit() // EXIT
        .transition(t)
      // get down to 0 if the first, or up the end if not
        .attr("x", (d) => this.x(d[0]))
        .attr("width", 0)
        //.remove();
    },

    renderChart() {
      const $this = this,
            data = this.data;
      const chart = this.chart;
      // using 2 transitions makes things easier to follow
      // (the removal / repositioning will be slightly delayed)
      const t = d3.transition(),
            t_ = d3.transition();
      // don't animate anything the first time
      if (this._rendered) {
        t.duration(750);
        t_.duration(350);
      }
      else {
        t.duration(0);
        t_.duration(0);
        this._rendered = true;
      }

      // resize the chart to fit the data
      this.xheight = Math.max(this.minHeight, // TODO: lose min-height?
                              this.itemHeight * data.length);
      // TODO: decide what to do with this:
      // - keep it immutable to max?
      // - jump suddenly at transition end?
      // - animate?
      // anyway, if we need extra-room, take immediate action
      this.height = Math.max(this.height, this.xheight)

      // most important thing first: animate the line!
      chart.select(".domain line")
        .transition(t)
        .attr("y2", this.xheight);

      /*
       * main stuff
       */
      const beneficiaries = chart
	    .selectAll("g.beneficiary")
            .data(data, (d) => d.name); /* JOIN */

      // insert the rows instead of appending
      // (makes sure the domain line stays on top)
      const bentered = beneficiaries.enter().insert("g") /* ENTER */
        .attr("class", (d) => "beneficiary " + d.id)
        .attr("transform", `translate(0,${this.xheight})`)

      bentered.merge(beneficiaries) /* ENTER _and_ UPDATE */
        .transition(t)
        .attr("opacity", 1)
        .attr("transform", (d) => `translate(0,${this.y(d.id)})`);

      beneficiaries.exit() /* EXIT */
        .transition(t)
        .attr("opacity", 0)
        .attr("transform", `translate(0,${this.xheight})`)
        // don't remove, save some dom operations
        //.remove();

      /*
       *
       */
      bentered.append("title").text(
        (d) => d.map(
          (d_) => d_.fm + ":\t" + this.format(d_.value)
        ).join("\n")
      )
      // draw a transparent rectangle to get continuos mouse-overing
      bentered.append("rect")
        .attr("class", "_fill")
        .attr("width", this.width)
        .attr("height", this.y.bandwidth())

      /*
       * render the "legend" part
       */
      // (it's not really a legend 'cause it's part of the row. you get it.)
      const _padding = 5, // TODO: propify
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
        .text((d) => d.name)
        .attr("x", - _padding)
      // v-align
        .attr("y", this.y.bandwidth() * this.y.paddingInner())
        .attr("dy", ".32em"); // magical self-centering offset

      country.append("use")
        .attr("xlink:href", (d) => `#${get_flag_name(d.name)}`)
        .attr("width", _flag.w)
        .attr("height", _flag.h);

      /*
       * render data items
       */
      const items = bentered.append("g") // we're still in ENTER here,
            .attr("class", "items")
            .attr("transform", (d) => `translate(${this.reserved},0)`);

      // but we want to run the item rendering both in ENTER and UPDATE
      items.merge(beneficiaries.select("g.items"))
        .transition(t_)
        .call(this.renderItems);
      // aand we also want to run it in EXIT, but with empty data
      // (normally the old data gets sent, so the items don't get disappeared)
      beneficiaries.exit().each( (d) => (d.splice(0)) )
                   .select("g.items")
        .transition(t_)
        .call(this.renderItems);

      /*
       * and finally, events
       */
      bentered
        .on("click", function (d) {
          $this.toggleBeneficiary(d.id, this);
        });
    },

    handleFilterFm() {
      this.render();
    },
  },
});

</script>
