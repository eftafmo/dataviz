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
    <dropdown filter="region" title="Select a beneficiary state" :items="data"></dropdown>
  </div>
  <svg width="100%" :height="height + 'px'">
    <filter id="grayscale">
      <feColorMatrix type="matrix"
                     values="0.3333 0.3333 0.3333 0 0
                             0.3333 0.3333 0.3333 0 0
                             0.3333 0.3333 0.3333 0 0
                             0      0      0      1 0" />
    </filter>
    <g class="chart" :transform="`translate(${legendWidth},0)`">
      <g class="beneficiaries" />
      <line class="domain" />
    </g>
  </svg>
</div>
</template>


<style lang="less">
// defs
@beneficiary_highlight: #e6e6e6;

.beneficiaries-viz {

  @media (min-width:1400px){
      max-width: 100%;
  }

  @media (max-width: 1000px) {
      max-width: 100%;
  }

  max-width: 70%;

  svg {
    width: 100%;

    // NOTE: this influences all inner layout
    // (the chart is em-based!)
    font-size: 1.6rem;
  }

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

  .chart {
    line.domain {
      stroke: #ccc;
      shape-rendering: crispEdges;
      // don't interrupt hovering the items
      pointer-events: none;
    }

    // NOTE: if you change the structure of this, you must also change
    // how legendWidth() is computed
    .beneficiaries .beneficiary {
      cursor: pointer;
      pointer-events: all;

      rect {
        shape-rendering: crispEdges;
        stroke: none;
      }

      rect.bg {
        fill: none;
      }

      &:hover {
        .fms rect.bg {
          fill: @beneficiary_highlight;
        }
      }

      text {
        font-size: .8em;
        font-family: 'Open sans', sans-serif;
        text-anchor: end;
      }
    }
  }
}
</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';
import {colour2gray} from 'js/lib/util';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import CSVReadingMixin from './mixins/CSVReading';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin, {COUNTRIES, get_flag_name} from './mixins/WithCountries';
import TooltipMixin from './mixins/TooltipMixin';


export default Vue.extend({
  mixins: [
    BaseMixin, CSVReadingMixin,
    ChartMixin, WithFMsMixin, WithCountriesMixin, TooltipMixin,
  ],

  data() {
    return {
      label_colour: "#333",
      layout: {
        // these are all em-based values
        itemHeight: 1.4,
        itemPadding: .6,
        barHeight: .9,
        flagHeight: 1.4,
        flagPadding: .4,
      },

      // an amazing way to calculate "Czech Republic"
      longestTxt: d3.values(COUNTRIES).reduce(function(longest, country) {
        return longest.length > country.name.length ? longest : country.name;
      }, ''),
    };
  },

  computed: {
    // turn all dimensions to px, and round them 'cause things get messy otherwise
    itemHeight() { return Math.round(this.fontSize * this.layout.itemHeight); },
    itemPadding() { return Math.round(this.fontSize * this.layout.itemPadding); },
    barHeight() { return Math.round(this.fontSize * this.layout.barHeight); },
    flagHeight() { return Math.round(this.fontSize * this.layout.flagHeight); },
    flagPadding() { return Math.round(this.fontSize * this.layout.flagPadding); },

    barPadding() {
      const padding = (this.itemHeight - this.barHeight) / 2;
      // we really, really want this to be an int

      if (parseInt(padding) != padding) {
        // uh'oh. use some brute force
        this.layout.itemHeight = (Math.ceil(padding) * 2 + this.barHeight) / this.fontSize;
        return this.barPadding;
      }
      return padding;
    },

    flagWidth() {
      // this could be smarter, but whatever
      const w = 60, h = 40; // the image dimensions
      return this.flagHeight * w / h;
    },

    flagBoundingWidth() {
      return this.flagWidth + 2 * this.flagPadding;
    },

    width() {
      return this.svgWidth;
    },

    height() {
      // this is used in the template, so vue will try to call it
      // before ready
      if (!this.isReady) return 0;

      const count = this.data.length,
            height = this.itemHeight * count +
                     this.itemPadding * (count - 1);

      // only resize the chart if there's not enough drawing room
      // (prevents the footer from dancing around during filtering)
      this._height = this._height ? Math.max(this._height, height) :
                                    height;
      return this._height;
    },

    legendWidth() {
      // compute the length of the largest text item in the "legend"
      if (!this.isReady) return 0;

      // this has to respect the structure of a beneficiary <g>
      const fakeB = this.chart.select(".beneficiaries").append("g").attr("class", "beneficiary");
      const txt = fakeB.append("g").attr("class", "label").append("text").attr("visibility", "hidden");

      txt.text(this.longestTxt);
      const txtwidth = txt.node().getBBox().width;
      fakeB.remove();

      // add a tiny bit of leeway, because custom font might not load so fast
      return txtwidth * 1.1 + this.flagBoundingWidth;
    },

    x() {
      return d3.scaleLinear()
               .range([0, this.width - this.legendWidth - this.barPadding])
               .domain([0, d3.max(this.data, (d) => d.total)]);
    },

    y() {
      const _height = this.itemHeight + this.itemPadding;
      return (d, i) => i * _height;
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
  },

  methods: {
    renderFms(context) {
      // this could receive both a selection and a transition
      const selection = context.selection ? context.selection() : context,
            t = context;

      // handle the bg, it's already created
      selection.select("rect.bg")
        .attr("width", (d) => this.x(d.total) + this.barPadding )
        .attr("height", this.barHeight + this.barPadding * 2);

      // the real deal
      const items = selection.selectAll("rect.fm").data(
        (d) => d, // re-bind local data (to create a join)
        (d) => d.fm // the key
      );

      items.enter().append("rect") // ENTER-only
        .attr("class", (d) => "fm " + d.fm)
        .attr("fill", (d) => this.colour(d.fm))
        // adding a stroke as well prevents what looks like a sub-pixel gap
        // between fms. but needs to be done for background too, so, TODO
        //.attr("stroke", (d) => this.colour(d.fm))
        .attr("y", this.barPadding)
        .attr("height", this.barHeight)

      .merge(items) // ENTER + UPDATE
        .transition(t)
        .attr("x", (d) => this.x(d[0]))
        .attr("width", (d) => this.x(d[1]) - this.x(d[0]));

      items.exit() // EXIT
        .transition(t)
        // shrink down to 0 if the first item, or expand to the end otherwise
        .attr("x", (d) => this.x(d[0]))
        .attr("width", 0)
        //.remove();

      // handle the fg, it's already created
      selection.select("rect.fg")
        .attr("width", (d) => this.x(d.total) + this.barPadding )
        .attr("height", this.barHeight + this.barPadding * 2);

    },

    renderChart() {
      const $this = this,
            data = this.data;
      const chart = this.chart;
      // using 2 transitions makes things easier to follow
      // (the removal / repositioning will be slightly delayed)
      const t = this.getTransition(750),
            t_ = this.getTransition(350);

      // most important thing first: animate the line!
      chart.select("line.domain")
        .transition(t)
        .attr("y2", this.height);

      /*
       * main stuff
       */
      const beneficiaries = chart.select(".beneficiaries")
            .selectAll("g.beneficiary")
            .data(data, (d) => d.name ); /* JOIN */

      const bentered = beneficiaries.enter().append("g") /* ENTER */
        .attr("class", (d) => "beneficiary " + d.id)
        .attr("transform", `translate(0,${this.height})`)

      bentered.merge(beneficiaries) /* ENTER _and_ UPDATE */
        .transition(t)
        .attr("opacity", 1)
        .attr("transform", (d, i) => `translate(0,${this.y(d, i)})`);

      beneficiaries.exit() /* EXIT */
        .transition(t)
        .attr("opacity", 0)
        .attr("transform", `translate(0,${this.height})`)
        // don't remove, save some dom operations
        //.remove();

      /*
       *
       */
      /*
       * render the row labels
       */
      const country = bentered.append("g")
              .attr("class", "label")
              .attr("transform", `translate(-${this.flagBoundingWidth},0)`);

      // place a transparent thingie behind the flag to aid continuous hovering
      country.append("rect").attr("class", "bg")
        .attr("width", this.flagBoundingWidth)
        .attr("height", this.itemHeight);

      country.append("text")
        .text((d) => d.name)
        .attr("fill", this.label_colour)
        // v-align
        .attr("y", this.itemHeight / 2)
        .attr("dy", ".33em"); // magin self-centering offset

      country.append("use")
        .attr("xlink:href", (d) => `#${get_flag_name(d.id)}`)
        .attr("x", this.flagPadding)
        .attr("y", (this.itemHeight - this.flagHeight) / 2)
        .attr("width", this.flagWidth)
        .attr("height", this.flagHeight);

      /*
       * render fm data
       */
      const fms = bentered.append("g") // we're still in ENTER here,
            .attr("class", "fms")

      // while here, draw a full-width rectangle used for mouse-over effects.
      // this will look like a border around the fms
      const bg = fms.append("rect").attr("class", "bg"); // continued in renderFms

      // we want to run the item rendering both in ENTER and UPDATE
      fms.merge(beneficiaries.select("g.fms"))
        .transition(t_)
        .call(this.renderFms);

      // append a rect to prevent the hover mouseover event to propagate to children
      const fg = fms.append("rect").attr("class", "fg").style('visibility', 'hidden')
        .attr("width", (d) => this.x(d.total) + this.barPadding )
        .attr("height", this.barHeight + this.barPadding * 2);

      // aand we also want to run it in EXIT, but with empty data
      // (normally the old data gets sent, so the fms don't get disappeared)
      beneficiaries.exit().each( (d) => (d.splice(0)) )
                   .select("g.fms")
        .transition(t_)
        .call(this.renderFms);

      // add tooltip
      let tip = d3.tip()
            .attr('class', 'd3-tip benef')
           .html(function(d){
             return "<div class='title-container'>"
              + "<img src=/assets/imgs/" + get_flag_name(d.id) + ".png/>"
              + "<span class='name'>"+ d.name + "</span></div>"
              // TODO: 'grants' word should be taken from data
              + d.map((d_) => d_.fm + " grants" + ":\t" + $this.format(d_.value)).join('\n')
              + " <span class='action'>~Click to filter by beneficiary state</span>"
           })

      tip.offset(function(e) {
            return [-20,  d3.event.layerX - $this.legendWidth - this.getBBox().width/2]
       }).direction('n');


       chart.call(tip)

       fg.on('mousemove', tip.show)
          .on('mouseout', tip.hide);
      /*
       * and finally, events
       */
      bentered
        .on("click", function (d) {
          $this.toggleBeneficiary(d.id, this);
        });
    },

    handleFilterRegion(val) {
      // gray out sibling beneficiaries (or activate them all)
      const beneficiaries = this.chart
                                .select("g.beneficiaries")
                                .selectAll("g.beneficiary")
                                .transition(this.getTransition());

      const _inactivecolour = (c) => colour2gray(c, this.inactive_opacity);
      const _activate = (selection, yes) => {
        // activates or deactivates:

        // the text
        selection.select("g.label").select("text")
          .attr("fill",
                yes ?
                  this.label_colour :
                  _inactivecolour(this.label_colour)
          );

        // the flag. TODO: clone the filter per-element,
        // and transition its matrix

        selection.select("g.label").select("use")
                 .attr("filter", yes ? null : "url('#grayscale')")
                 .attr("opacity", yes ? 1 : this.inactive_opacity);

        // the fm bars
        selection.select("g.fms").selectAll("rect.fm")
          .attr("fill",
                yes ?
                  (d) => this.colour(d.fm) :
                  (d) => _inactivecolour(this.colour(d.fm))
          );
      };

      const activate = (selection) => _activate(selection, true),
            deactivate = (selection) => _activate(selection, false);

      beneficiaries.filter(
        (d) => val === null || d.id == val
      ).call(activate);

      beneficiaries.filter(
        (d) => val !== null && d.id != val
      ).call(deactivate);
    },

    handleFilterFm() {
      this.render();
    },

    changedDimension() {
      // re-render on dimensions change
      // (but don't mess with the initial render)
      if (!this.rendered) return;
      // and don't animate things
      this.rendered = false;
      this.render();
    },
  },

  watch: {
    svgWidth: "changedDimension",
    fontSize: "changedDimension",
  },
});

</script>
