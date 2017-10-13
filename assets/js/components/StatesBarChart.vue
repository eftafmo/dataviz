<template>
<div :class="classNames">
  <slot name="title" v-if="!this.embedded"></slot>
  <dropdown v-if="hasData" :filter="state_type" title="No filter selected" :items="nonzero"></dropdown>

  <chart-legend
      class="inline"
      :items="legend_items"
      :click-func="legendClickFunc"
      :format-func="legendFormatFunc"
  ></chart-legend>

  <svg width="100%" :height="height + 'px'" class="chart">
    <defs>
      <filter id="drop-shadow">
        <feGaussianBlur in="SourceAlpha" stdDeviation="1"/>
        <feOffset dx="0" dy="0" result="offsetblur"/>
        <feFlood flood-color="rgba(0,0,0,0.3)"/>
        <feComposite in="offsetblur" operator="in"/>
        <feMerge>
          <feMergeNode/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
      <filter id="inactive">
        <feColorMatrix type="matrix"
                       :values="matrix2value(grayscaleMatrix)" />
      </filter>
      <filter id="active">
        <feColorMatrix type="matrix"
                       :values="matrix2value(normalMatrix)" />
      </filter>
      <filter id="activating">
        <feColorMatrix type="matrix" />
      </filter>
      <filter id="inactivating">
        <feColorMatrix type="matrix" />
      </filter>
    </defs>
    <g :transform="`translate(${legendWidth},0)`">
      <g class="states" />
      <line class="domain" />
    </g>
  </svg>
</div>
</template>


<style lang="less">
// defs
@state_highlight: #e6e6e6;

.dataviz .viz.states {
  position: relative;

  @media (min-width:1400px){
      max-width: 100%;
  }

  @media (max-width: 1000px) {
      max-width: 100%;
  }

  @media (min-width: 1000px) and (max-width: 1400px) {
      select {
        right: -45%;
      }
  }

  max-width: 70%;

  svg {
    width: 100%;

    // NOTE: this influences all inner layout
    // (the chart is em-based!)
    font-size: 1.6rem;
  }

  .legend {
    .fm {
      display: inline-block;
    }
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
    .states .state {
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
        .divs rect.bg {
          fill: @state_highlight;
        }
      }

      text {
        font-size: .8em;
        font-family: 'Arial', 'Open sans', sans-serif;
        text-anchor: end;
      }

      g.flag {
        filter: url("#drop-shadow");
      }
    }
  }
}
</style>


<script>
import * as d3 from 'd3';
import {slugify} from 'js/lib/util';

import Chart from './Chart';

import WithCountriesMixin, {get_flag_name} from './mixins/WithCountries';
import WithTooltipMixin from './mixins/WithTooltip';

import Legend from './includes/Legend';


export default Chart.extend({
  type: "states",

  mixins: [
    WithCountriesMixin,
    WithTooltipMixin,
  ],

  components: {
    "chart-legend": Legend,
  },

  beforeCreate() {
    this.grayscaleMatrix = [
        [0.3333, 0.3333, 0.3333, 0, 0],
        [0.3333, 0.3333, 0.3333, 0, 0],
        [0.3333, 0.3333, 0.3333, 0, 0],
        [0     , 0     , 0     , 1, 0]
    ];
    this.normalMatrix = [
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0]
    ];
  },

  data() {
    return {
      state_type: undefined, // children must define this (beneficiary / donor)
      //div_types: undefined, // required, an array of dictionaries with {id, colour}

      label_colour: "#333",
      layout: {
        // these are all em-based values
        itemHeight: 1.4,
        itemPadding: .6,
        barHeight: .9,
        flagHeight: 1.4,
        flagPadding: .4,
      },
    };
  },

  created() {
    // group by and don't filter / aggregate by beneficiary / donor
    const groupcol = this.state_type;

    let idx;

    idx = this.filter_by.indexOf(groupcol);
    if (idx !== -1)
      this.filter_by.splice(idx, 1);

    this.aggregate_by.push(
        { source: groupcol, destination: "id" }
    );

    idx = this.aggregate_on.findIndex(x => x.source == groupcol);
    if (idx !== -1) this.aggregate_on.splice(idx, 1);

    // remember the current height
    this._height = 0;
  },

  computed: {
    legendClickFunc() {
      return null;
    },

    legendFormatFunc() {
      return null;
    },

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
      return this.chartWidth;
    },

    itemsHeight() {
      // this is used in the template, so vue will try to call it
      // before ready
      if (!this.isReady) return 0;

      const count = this.data.filter( (d) => d.total != 0 ).length,
            height = this.itemHeight * count +
                     this.itemPadding * (count - 1);

      return height;
    },

    height() {
      // only resize the chart if there's not enough drawing room
      // (prevents the footer from dancing around during filtering)
      this._height = Math.max(this._height, this.itemsHeight)
      return this._height;
    },

    longestText() {
      return this.longestCountry
    },

    legendWidth() {
      // compute the length of the largest text item in the "legend"
      if (!this.isReady) return 0;

      // this has to respect the structure of a state <g>
      const fakeS = this.chart.select(".states").append("g").attr("class", "state");
      const txt = fakeS.append("g").attr("class", "label").append("text").attr("visibility", "hidden");

      txt.text(this.longestText);
      const txtwidth = txt.node().getBBox().width;
      fakeS.remove();

      // add a tiny bit of leeway, because custom font might not load so fast
      return txtwidth * 1.1 + this.flagBoundingWidth;
    },

    types() {
      throw new Error("Not implemented");
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
      if (!this.hasData) return [];

      const aggregated = this.aggregated;

      const out = [];
      // we'll use this to preserve order, and as a basis for each bar item

      for (const sid in this.STATES) {
        const state = this.STATES[sid],
              data = aggregated[sid] || {};

        // merge in state data
        const item = Object.assign(
          {
            data: [],
            total: 0,
          },
          state,
          data
        )

        // build series data
        let oldend = 0;
        for (const type of this.div_types) {
          const current = this.valuefunc(item, type.id),
                newend = oldend + current;

          item.total += current;
          item.data.push(Object.assign(
            {
              value: current,
              d: [oldend, newend],
            },
            type
          ))

          oldend = newend
        }

        out.push(item)
      }

      return out;
    },

    nonzero() {
      return this.data.filter( (d) => d.total != 0 );
    },

    total() {
      return this.data.reduce((total, item) => total + item.total, 0)
    },

    totals() {
      // like above, but grouped by type
      const state = this.filters[this.state_type]
      return this.data.reduce(
        (totals, item) => {
          // when filtering by state, ignore other states
          if (state && item.id != state) return totals
          for (const type of item.data) {
            const id = type.id,
                  value = type.value;
            let total = totals[id] || 0
            totals[id] = total + value
          }
          return totals
        }, {})
    },

    legend_items() {
      // just the totals merged into the types
      if (!this.isReady) return []
      const out = {}
      for (const t in this.types) {
        out[t] = Object.assign({
          value: this.totals[t],
        }, this.types[t])
      }

      // return an array though
      return d3.values(out)
    },
  },

  methods: {
    matrix2value(matrix) {
      return matrix.map( (x) => x.join(" ") ).join("\n");
    },

    valuefunc(item, type) {
      // given an item and the division id, return the value for series data
      throw new Error("Not implemented")
    },

    renderStateData(context) {
      // this could receive both a selection and a transition
      const selection = context.selection ? context.selection() : context,
            t = context == selection ? this.getTransition() : context;


      // handle the bg, it's already created
      selection.select("rect.bg")
        .attr("width", (d) => this.x(d.total) + this.barPadding )
        .attr("height", this.barHeight + this.barPadding * 2);

      // the real deal
      const divs = selection.selectAll("g.div")
                            .data( (b) => b.data, (d) => d.id );

      divs.enter() // ENTER-only
        .append("g")
        .attr("class", (d) => "div " + d.id )
        .attr("fill", (d) => (
          this.filters[this.state_type] === null ||
          this.filters[this.state_type] == d[this.state_type] ?
          d.colour : this.inactivecolour(d.colour)
        ) )
        // adding a stroke as well prevents what looks like a sub-pixel gap
        // between divs. but needs to be done for background too, so, TODO
        //.attr("stroke", (d) => d.colour )
        .append("rect")
        .attr("y", this.barPadding)
        .attr("height", this.barHeight)
        .attr("x", (d) => this.x(d.d[0]) )
        .attr("width", (d) => this.x(d.d[1]) - this.x(d.d[0]) );

      divs.select("rect") // UPDATE
        .transition(t)
        .attr("x", (d) => this.x(d.d[0]) )
        .attr("width", (d) => this.x(d.d[1]) - this.x(d.d[0]) );
    },

    createTooltip() {
      const $this = this;
      // add tooltip
      let tip = d3.tip()
          .attr('class', 'dataviz-tooltip state')
          .html(this.tooltipTemplate)
          .direction('n')
          .offset(function(d) {
            const zeroed = (-this.getBBox().width / 2
                            -this.getBBox().x);

            return [
              -$this.itemHeight * 0.9,
              Math.max(zeroed,
                       // an amazing way to calculate the mouse position for dataviz-tooltip
                       d3.event.clientX
                       -$this.chart.node().getBoundingClientRect().left
                       + zeroed
                       -$this.legendWidth
                      )
            ];
          });

       this.tip = tip;
       this.chart.call(this.tip)
    },

    renderChart() {
      const $this = this,
            data = this.data;
      const chart = this.chart;
      // using 2 transitions makes things easier to follow
      // (the removal / repositioning will be slightly delayed)
      const t = this.getTransition(),
            t_ = this.getTransition(this.duration / 2);

      // most important thing first: animate the line!
      chart.select("line.domain")
        .transition(t)
      // the line height needs to depend on the data length for the div filtering
        .attr("y2", this.itemsHeight);

      /*
       * main stuff
       */
      const states = chart.select(".states")
            .selectAll("g.state")
            .data(data, (d) => d.id );

      const sentered = states.enter().append("g")
        .attr("class", (d) => "state " + d.id)
        .attr("opacity", 0)
        .attr("transform", `translate(0,${this.height})`);

      const sboth = states.merge(sentered);

      sboth.filter( (d) => d.total != 0 ) // entered items can also be 0-ed
        .transition(t)
        .attr("opacity", 1)
        .attr("transform", (d, i) => `translate(0,${this.y(d, i)})`);

      sboth.filter( (d) => d.total == 0 ) /* exit substitute */
        .transition(t)
        .attr("opacity", 0)
        // translate items out of the viewport.
        // disabled because it only makes sense with ordered values.
        //.attr("transform", `translate(0,${this.height})`)

      /*
       * render the row labels
       */
      const country = sentered.append("g")
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
        .attr("dy", ".33em"); // magical self-centering offset

      country.append("g")
        .attr("class", "flag")
      .append("use")
        .attr("xlink:href", (d) => `#${get_flag_name(d.id)}`)
        .attr("x", this.flagPadding)
        .attr("y", (this.itemHeight - this.flagHeight) / 2)
        .attr("width", this.flagWidth)
        .attr("height", this.flagHeight)

      /*
       * render div data
       */
      const divs = sentered.append("g") // we're still in ENTER here,
            .attr("class", "divs")

      // while here, draw a full-width rectangle used for mouse-over effects.
      // this will look like a border around the divs
      const bg = divs.append("rect").attr("class", "bg"); // continued in renderStateData

      // we want to run the item rendering both in ENTER and UPDATE
      divs.merge(states.select("g.divs"))
        .transition(t_)
        .call(this.renderStateData);

      /*
       * set the active / inactive colours if necessary
       * (after the divs were drawn)
       */
      sentered
        .call(this.renderActive);

      /*
       * and finally, events
       */
      sentered
        .on("click", function (d) {
          $this.clickFunc(d, this);
        })
        // tooltip events
        .on('mouseenter', this.tip.show)
        .on('mouseleave', this.tip.hide);
    },

    renderActive(states) {
      const $this = this;

      const _activate = (context, yes) => {
        const selection = context.selection ? context.selection() : context,
              t = context == selection ? this.getTransition() : context;

        // activates or deactivates:

        // the text
        selection.select("g.label").select("text")
          .transition(t)
          .attr("fill",
                yes ?
                  this.label_colour :
                  this.inactivecolour(this.label_colour)
          );

        // the flag
        selection.select("g.label").select("g.flag")
          .transition(t)
          .attr("opacity", yes ? 1 : this.inactive_opacity)
        .select("use")
          .on("start", function() {
            const current = d3.select(this).style("filter")
                              .replace(/url\([\'\"]?#(\w+)[\'\"]?\)/, "$1");

            if (yes && current == "inactive")
              d3.select(this).style("filter", "url('#activating')");

            else if (!yes && current == "active")
              d3.select(this).style("filter", "url('#inactivating')");
          })
          .on("end", function() {
            d3.select(this).style(
              "filter", `url('#${yes ? "active" : "inactive"}')`
            );
          });

        // the filters' matrices used by the flags
        const interpolateActivating = d3.interpolateArray(
                this.grayscaleMatrix, this.normalMatrix),
              interpolateInactivating = d3.interpolateArray(
                this.normalMatrix, this.grayscaleMatrix);

        this.chart.select("defs #activating feColorMatrix")
          .attr("values", this.matrix2value(this.grayscaleMatrix))
          .transition(t)
          .attrTween("values", function(d) {
            return function(x) {
              return $this.matrix2value(interpolateActivating(x));
            };
          });

        this.chart.select("defs #inactivating feColorMatrix")
          .attr("values", this.matrix2value(this.normalMatrix))
          .transition(t)
          .attrTween("values", function(d) {
            return function(x) {
              return $this.matrix2value(interpolateInactivating(x));
            };
          });

        // the div bars
        selection.select("g.divs").selectAll(".div")
          .transition(t)
          .attr("fill", (d) => yes ? d.colour : this.inactivecolour(d.colour))
      };

      const activate = (selection) => _activate(selection, true),
            deactivate = (selection) => _activate(selection, false);

      const val = this.filters[this.state_type];

      states.filter(
        (d) => val === null || d.id == val
      ).call(activate);

      states.filter(
        (d) => val !== null && d.id != val
      ).call(deactivate);
    },

    handleStateFilter() {
      // call this when filtered by beneficiary / donor
      // gray out sibling states (or activate them all)
      const states = this.chart
                         .select("g.states")
                         .selectAll("g.state");

      states
        .transition(this.getTransition())
        .call(this.renderActive);
    },

    changedDimension() {
      // re-render on dimensions change
      // (but don't mess with the initial render)
      if (!this.isReady) return;
      // and don't animate things
      this.render(true);
    },
  },

  watch: {
    chartWidth: "changedDimension",
    fontSize: "changedDimension",
  },
});

</script>
