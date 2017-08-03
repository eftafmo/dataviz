<template>
<div class="beneficiaries-viz">
   <h2>{{title}}</h2>
    <dropdown v-if="rendered" filter="beneficiary" title="No filter selected" :items="nonzero"></dropdown>
  <div v-if="hasData" class="legend">
    <fm-legend :fms="FMS" class="clearfix">
    </fm-legend>
  </div>
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

import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin, {get_flag_name} from './mixins/WithCountries';
import WithTooltipMixin from './mixins/WithTooltip';


export default Chart.extend({
  mixins: [
    WithFMsMixin, WithCountriesMixin,
    WithTooltipMixin,
  ],

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
      filter_by: ["fm", "sector", "area"],

      label_colour: "#333",
      layout: {
        // these are all em-based values
        itemHeight: 1.4,
        itemPadding: .6,
        barHeight: .9,
        flagHeight: 1.4,
        flagPadding: .4,
      },
      title: 'Funding across beneficiary states'
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
      this._height = this._height ? Math.max(this._height, this.itemsHeight) :
                                    this.itemsHeight;
      return this._height;
    },

    legendWidth() {
      // compute the length of the largest text item in the "legend"
      if (!this.isReady) return 0;

      // this has to respect the structure of a beneficiary <g>
      const fakeB = this.chart.select(".beneficiaries").append("g").attr("class", "beneficiary");
      const txt = fakeB.append("g").attr("class", "label").append("text").attr("visibility", "hidden");

      txt.text(this.longestBeneficiary);
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
      const aggregated = this.aggregate(
        this.filtered,
        ['beneficiary', 'fm'],
        [
          'allocation',
          'project_count',
          //{source: 'sector', destination: 'sectors', type: String},
        ],
        false
      );

      const out = [];
      // we'll use this to preserve order, and as a basis for each bar item
      const fms = d3.values(this.FMS);

      for (const bid in this.BENEFICIARIES) {
        const data = aggregated[bid] || {};

        const item = {
          data: [],
          total: 0,
          //sectors: d3.set(),
        };

        Object.assign(item, this.BENEFICIARIES[bid]);

        let oldend = 0; // used for series data
        for (const fm of fms) {
          const values = data[fm.name] || {
            beneficiary: bid,
            allocation: 0,
            project_count: 0,
          },
                allocation = values.allocation,
                project_count = values.project_count;

          item.total += allocation;

          delete values.fm;
          Object.assign(values, fm);

          const newend = oldend + allocation;
          // the series data. naming is hard.
          values.d = [oldend, newend];
          oldend = newend;

          item.data.push(values);
        }
        out.push(item);
      }

      return out;
    },

    nonzero() {
      return this.data.filter( (d) => d.total != 0 );
    },
  },

  methods: {
    matrix2value(matrix) {
      return matrix.map( (x) => x.join(" ") ).join("\n");
    },

    renderBeneficiaryData(context) {
      // this could receive both a selection and a transition
      const selection = context.selection ? context.selection() : context,
            t = context == selection ? this.getTransition() : context;


      // handle the bg, it's already created
      selection.select("rect.bg")
        .attr("width", (d) => this.x(d.total) + this.barPadding )
        .attr("height", this.barHeight + this.barPadding * 2);

      // the real deal
      const fms = selection.selectAll("g.fm")
                           .data( (b) => b.data, (d) => d.id );

      fms.enter() // ENTER-only
        .append("g")
        .attr("class", (d) => "fm " + d.id )
        .attr("fill", (d) => (
          this.filters.beneficiary === null || this.filters.beneficiary == d.beneficiary ?
          d.colour : this.inactivecolour(d.colour)
        ) )
        // adding a stroke as well prevents what looks like a sub-pixel gap
        // between fms. but needs to be done for background too, so, TODO
        //.attr("stroke", (d) => d.colour )
        .append("rect")
        .attr("y", this.barPadding)
        .attr("height", this.barHeight)
        .attr("x", (d) => this.x(d.d[0]) )
        .attr("width", (d) => this.x(d.d[1]) - this.x(d.d[0]) );

      fms.select("rect") // UPDATE
        .transition(t)
        .attr("x", (d) => this.x(d.d[0]) )
        .attr("width", (d) => this.x(d.d[1]) - this.x(d.d[0]) );
    },

    tooltipTemplate(d) {
      // TODO: this is getting beyond silly.
      const data = d.data
                    .filter( (x) => x.allocation != 0 );
      const datatxt = data
        .map( (x) => `
            <li>${ x.name } : ${ this.currency(x.allocation) }</li>
        ` )
        .join("");

      return `
        <div class="title-container">
        <svg>
          <use xlink:href="#${this.get_flag_name(d.id)}" />
        </svg>
          <span class="name">${d.name}</span>
        </div>
        <ul> ${ datatxt } </ul>
        <span class="action">Click to filter by beneficiary state</span>
      `;
    },

    createTooltip() {
      const $this = this;
      // add tooltip
      let tip = d3.tip()
          .attr('class', 'd3-tip benef')
          .html(this.tooltipTemplate)
          .direction('n')
          .offset(function(d) {
            const zeroed = (-this.getBBox().width / 2
                            -this.getBBox().x);

            return [
              -$this.itemHeight * 0.9,
              Math.max(zeroed,
                       // an amazing way to calculate the mouse position for d3-tip
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
      // the line height needs to depend on the data length for the FM filtering
        .attr("y2", this.itemsHeight);

      /*
       * main stuff
       */
      const beneficiaries = chart.select(".beneficiaries")
            .selectAll("g.beneficiary")
            .data(data, (d) => d.id );

      const bentered = beneficiaries.enter().append("g")
        .attr("class", (d) => "beneficiary " + d.id)
        .attr("opacity", 0)
        .attr("transform", `translate(0,${this.height})`);

      const bboth = beneficiaries.merge(bentered);

      bboth.filter( (d) => d.total != 0 ) // entered items can also be 0-ed
        .transition(t)
        .attr("opacity", 1)
        .attr("transform", (d, i) => `translate(0,${this.y(d, i)})`);

      bboth.filter( (d) => d.total == 0 ) /* exit substitute */
        .transition(t)
        .attr("opacity", 0)
        // translate items out of the viewport.
        // disabled because it only makes sense with ordered values.
        //.attr("transform", `translate(0,${this.height})`)

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
       * render fm data
       */
      const fms = bentered.append("g") // we're still in ENTER here,
            .attr("class", "fms")

      // while here, draw a full-width rectangle used for mouse-over effects.
      // this will look like a border around the fms
      const bg = fms.append("rect").attr("class", "bg"); // continued in renderBeneficiaryData

      // we want to run the item rendering both in ENTER and UPDATE
      fms.merge(beneficiaries.select("g.fms"))
        .transition(t_)
        .call(this.renderBeneficiaryData);

      /*
       * set the active / inactive colours if necessary
       * (after the fms were drawn)
       */
      bentered
        .call(this.renderActive);

      /*
       * and finally, events
       */
      bentered
        .on("click", function (d) {
          $this.toggleBeneficiary(d, this);
        })
        // tooltip events
        .on('mouseenter', this.tip.show)
        .on('mouseleave', this.tip.hide);
    },

    renderActive(beneficiaries) {
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

        // the fm bars
        selection.select("g.fms").selectAll(".fm")
          .transition(t)
          .attr("fill", (d) => yes ? d.colour : this.inactivecolour(d.colour))
      };

      const activate = (selection) => _activate(selection, true),
            deactivate = (selection) => _activate(selection, false);

      const val = this.filters.beneficiary;

      beneficiaries.filter(
        (d) => val === null || d.id == val
      ).call(activate);

      beneficiaries.filter(
        (d) => val !== null && d.id != val
      ).call(deactivate);
    },

    handleFilterBeneficiary() {
      // gray out sibling beneficiaries (or activate them all)
      const beneficiaries = this.chart
                                .select("g.beneficiaries")
                                .selectAll("g.beneficiary");
      beneficiaries
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
    svgWidth: "changedDimension",
    fontSize: "changedDimension",
  },
});

</script>
