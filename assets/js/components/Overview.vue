<template>
<div :class="classNames">
  <chart-container :width="width" :height="height">
    <svg :viewBox="`0 0 ${width} ${height}`">
      <defs>
        <linearGradient id="link-gradient">
          <stop offset="10%"  stop-color="#ccc"/>
          <stop offset="90%" stop-color="#eee"/>
        </linearGradient>
      </defs>

      <g class="chart" :transform="`translate(${width / 2},${height / 2})`">
        <g class="fms"></g>
        <g class="beneficiaries"></g>
        <g class="links"></g>
      </g>
    </svg>

    <div v-if="hasData && aggregated.allocation" class="info">
      <transition name="fade">
        <div :style="{fontSize: fonts.top_text + 'px'}" class="heading" :key="changed">
          <p><span class="amount">{{ currency(aggregated.allocation) }}</span> spent on</p>
        </div>
      </transition>
      <div class="data-wrapper">
        <ul :style="{ 
        fontSize: fonts.middle_text + 'px', 
        paddingTop: circle_dimensions.padding_top + 'px',
        paddingBottom: circle_dimensions.padding_top + 'px',
        paddingLeft: circle_dimensions.padding_left + 'px',
        paddingRight: circle_dimensions.padding_left + 'px'
        }" 
         class="data">
          <li class="programmes"><span class="amount">{{ number(aggregated.programmes.size()) }}</span> Programmes</li>
          <li class="projects"><span class="amount">{{ number(aggregated.project_count) }}</span> Projects</li>
        </ul>
      </div>
      <div :style="{ fontSize: fonts.bottom_text + 'px' }" class="ending">
        <p>to reduce social and economic disparities across Europe and to strenghten bilateral relations in <span style="white-space:nowrap;">{{ period }}</span> funding period</p>
      </div>
    </div>


    <div v-if="!hasData || !aggregated.allocation" class="info">
      <transition name="fade">
        <div :style="{fontSize: fonts.top_text + 'px'}" class="heading" :key="changed">
          <p><span class="amount">No allocation available</span></p>
        </div>
      </transition>
      <div class="data-wrapper">
          <ul :style="{ 
          fontSize: fonts.middle_text + 'px', 
          paddingTop: circle_dimensions.padding_top + 'px',
          paddingBottom: circle_dimensions.padding_top + 'px',
          paddingLeft: circle_dimensions.padding_left + 'px',
          paddingRight: circle_dimensions.padding_left + 'px'
          }"  class="data">
            <li class="programmes"><span class="amount"></span>No programmes available</li>
            <li class="projects"><span class="amount"></span>No projects available</li>
          </ul>
      </div>
    </div>

  </chart-container>
</div>
</template>


<style lang="less">
// defs. shared with js below.
@source_stroke_opacity: .1;
@target_stroke_opacity: .5;

.dataviz .viz.overview {
  .chart {
    .fms > g.item, .beneficiaries > g.item {
      cursor: pointer;
      pointer-events: all;

      path.arc {
        fill: inherit;
        stroke: inherit;
        stroke-width: 1.34; // this should be equal to itemPadding
      }

      &:hover path.arc {
        stroke-opacity: 1;
      }

      path.blank {
        fill: none;
        //fill: palegoldenrod;
        stroke: none;
      }

      text {
        fill: #333;
        stroke: none;
        font-size: .5em;
      }

      &:hover text {
        fill: #000;
        stroke: #333;
        stroke-width: .2;
        stroke-opacity: .5;
      }
    }

    .fms > g.item path.arc {
      // this is set as attribute
      //stroke-opacity: @source_stroke_opacity;
    }

    .beneficiaries > g.item path.arc {
      fill: #ccc;
      stroke: #ccc;
      // this is set as attribute
      //stroke-opacity: @target_stroke_opacity;
    }

    .fms text {
      text-anchor: end;
    }

    .beneficiaries text {
      text-anchor: start;
    }

    .links {
      fill: url("#link-gradient");
      fill-opacity: .75;

      .highlighted {
        fill-opacity: 1;
      }
      .non-highlighted {
        fill-opacity: .25;
      }
    }
  }

  .info {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    //background-color: rgba(200,200,200,.1);

    text-align: center;
    font-size: 2rem;

    p, ul, li {
      margin: 0;
    }

    span.amount {
      display: block;
      font-weight: bold;
    }

    & > div {
      position: absolute;
      width: 50%;
      left: 25%;
      pointer-events: initial;
    }

    .heading {
      top: 5%;
      font-size: 1.5em;
      @media (max-width: 800px) {
        top: -29px;
        font-size: 95%;
      }

    }

    .data-wrapper {
      background: rgba(251, 251, 251, 0.8);
      background: linear-gradient(rgba(252, 252, 252, .75), rgba(227, 227, 227, .95));
      border: .2em solid white;
      border-radius: 100%;
      width: auto;
      transform: translate(-50%, -50%);
      top: 50%;
      left: 50%;
    }

    .data {
      list-style-type: none;
      padding: 0;

      & > li:not(:last-child) {
        margin-bottom: .5em;
      }

      .programmes {
        font-size: 1.5em;
        line-height: 1.6em;

        .amount {
          font-size: 1.8em;
        }
      }

      .projects {
        font-size: 1em;

        .amount {
          font-size: 2em;
        }
      }
    }

    .ending {
      bottom: 0%;
      font-size: 1.2em;
      @media(max-width: 800px){
      bottom: -19px;
      font-size: 59%;
      width: 100%;
      left: 0;
      }
    }

     @media(min-width:800px)and(max-width:1400px){
      .heading,
      .ending {
      }

      .ending {
        font-size: 105%;
      }
    }
  }


  .legend {
    position: absolute;
    left: 0;
    top: 0;
    @media(max-width: 800px){
      left: -1.5rem;
      top: -91px;
    }

    .fm span {
      width: 10px; height: 10px;
      display: inline-block;
    }
    li {
      list-style-type: none;
    }
  }

  .chart-container {
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 3rem;
    @media(max-width: 800px){
     margin-top: 1rem;
     margin-left: -1.5rem;
     margin-right: 0;
     width: calc(~"100% + 2.8rem")
    }
    @media (min-width: 800px)and (max-width:1000px){
      width: 84%;
    }
    @media (min-width:1000px) {
      width: 60%;
    }
  }
  &:not(.embedded){
    @media(min-width: 800px){
      margin-top: -5rem;
    }
  }

  &.embedded {
    .ending {
      left: 0;
      width: 100%;
    }
    .info {
      .data-wrapper {
        margin-top: -1rem;
      }
    }

      margin-top: 1rem!important;
    .chart-container {
      padding-bottom: 2rem;

      @media (min-width: 800px)and (max-width:1000px){
        width: 100%!important;
      }
      @media (min-width:1000px) {
        width: 100%!important;
      }
    }
  }
}
</style>


<script>
import * as d3 from 'd3';
import xchord from 'js/lib/x-chord';
import {slugify} from 'js/lib/util';

import Chart from './Chart';

import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';


export default Chart.extend({
  type: "overview",

  mixins: [
    WithFMsMixin, WithCountriesMixin
  ],

  data() {
    return {
      filter_by: ["fm", "beneficiary"],

      width: 500,

      padding: Math.PI / 2, // padding between main groups, in radians
      //itemPadding: 0,
      itemPadding: Math.PI / 180 / 3, // padding between items, in radians
      text_padding: .01, // percentage of width/height

      text_spacing: 2, // vertical spacing, in text-height units

      inner_radius: .85, // percentage of outer radius

      beneficiary_colour: "#ccc",

      source_stroke_opacity: .1,
      target_stroke_opacity: .5,

      // css properties that need to scale with the component container size
      fonts: {
        bottom_text: 0,
        top_text: 0,
        middle_text: 0,
      },

      circle_dimensions: {
        padding_left : 0,
        padding_top: 0,
      }
    };
  },

  computed: {
    height() {
      return this.width * Math.sin(Math.PI / 2 - this.padding / 2);
    },

    textDimensions() {
      // calculate maximum text width.
      // (fms group shows country names as well and uses the same font.)
      const fakeB = this.chart.select(".beneficiaries")
                        .append("g").attr("class", "item");
      const txt = fakeB.append("g").attr("class", "text")
                       .append("text").attr("visibility", "hidden");

      txt.text(this.longestCountry);
      const bounds = txt.node().getBBox();
      fakeB.remove();

      return {width: bounds.width, height: bounds.height};
    },

    textPadding() {
      return this.text_padding * this.width;
    },

    margin() {
      if (!this.isReady) return 0;
      return this.textDimensions.width + this.textPadding;
    },

    radius() {
      return this.width / 2 - this.margin;
    },

    innerRadius() {
      return this.radius * this.inner_radius;
    },

    linksRadius() {
      // links should be exactly itemPadding away from the arcs
      return this.innerRadius - this.radius * this.itemPadding;
    },

    textHeight() {
      return this.textDimensions.height;
    },

    textRadians() {
      return this.textHeight / this.radius;
    },

    textDegrees() {
      return this.textRadians / Math.PI * 180;
    },

    arc() {
      return d3.arc()
        .outerRadius(this.radius)
        .innerRadius(this.innerRadius);
    },


    blank() {
      const outerRadius = this.radius + this.margin,
            innerRadius = this.radius,
            txtheight = this.textHeight,
            txtrads = this.textRadians;

      const arcfunc = d3.arc()
        .outerRadius(outerRadius)
        .innerRadius(innerRadius);

      return function(d) {
        const coords = {startAngle: d.startAngle, endAngle: d.endAngle},
              height = (d.endAngle - d.startAngle) * innerRadius;

        if (height > txtheight) {
          // shave off a few pixels so this doesn't cover sibling cramped texts
          const center = (d.startAngle + d.endAngle) / 2;
          coords.startAngle = Math.min(
            d.startAngle + txtrads / 2, center - txtrads / 2
          );
          coords.endAngle = Math.max(
            d.endAngle - txtrads / 2, center + txtrads / 2
          );
        }
        return arcfunc(coords);
      }
    },

    link() {
      return d3.ribbon()
        .radius(this.linksRadius);
    },

    chord() {
      return xchord()
        .padding(this.padding)
        .itemPadding(this.itemPadding);
    },

    aggregated() {
      return this.aggregate(
        this.filtered,
        [],
        [
          'allocation', 'project_count',
          {source: 'programmes', type: Array},
        ],
        false
      );
    },

    data() {
      const matrix = [],
            dataset = this.aggregate(
              this.filtered, ['fm', 'beneficiary'], ['allocation'], false
            );

      // base the dataset on the constant list of FMs and beneficiaries,
      // to ensure 0-valued items exist regardless of filtering
      for (const fm of this.FM_ARRAY) {
        const fmdata = dataset[fm.name],
              allocations = Array();

        matrix.push(allocations);

        if (fmdata === undefined) {
          allocations.length = this.BENEFICIARY_ARRAY.length;
          allocations.fill(0);
          continue;
        }

        for (const bnf of this.BENEFICIARY_ARRAY) {
          const bnfdata = fmdata[bnf.id];
          allocations.push(bnfdata !== undefined ? bnfdata.allocation : 0);
        }
      }

      // if there are very small-valued items, we want to massage the data so
      // they occupy enough space to be usable (and avoid overlapping labels).
      //
      // what the code below does is calculate a reference delta to increment
      // the smalles value, and adjust all other items accordingly, so that
      // they a) preserve their order and
      //      b) keep a relative ratio from one to the next, while
      //      c) the total sum is preserved

      // no item should go below this (in percentage)
      const MIN = this.textRadians / (Math.PI * 2 - this.padding * 2) * 1.10

      const totals = matrix.reduce(
        (row, a) => row.map((b, i) => a[i] + b)
      )
      // for avg / stdev calculations we skip zeroes
      const _totals = totals.filter(x => x != 0)

      const sum = _totals.reduce((a, b) => a + b, 0),
            permitted = sum * MIN,
            minval = Math.min.apply(Math, _totals)

      if (sum == 0) return;

      // maybe there's nothing to do?
      if (minval >= permitted) return this.chord(matrix)

      const basedelta = permitted - minval,
            avg = sum / _totals.length

      const stdev = Math.sqrt(
        _totals.map(x => (x - avg) * (x - avg))
               .reduce((a, b) => a + b)

        / (_totals.length - 1)
      )

      // this is where the magic happens:
      const weights = totals.map(x => x == 0 ? 0 : (x - avg) / stdev)

      const minweight = Math.min.apply(Math, weights) // this corresponds to minval

      const deltas = totals.map((x, i) => x == 0 ? 0 : weights[i] * basedelta / minweight)

      for (const row of matrix) {
        row.forEach((x, i) => {
          if (x == 0) return 0

          row[i] = x + x / totals[i] * deltas[i]
        })
      }

      return this.chord(matrix)
    },
  },

  methods: {
    computeDimensions(event) {

      //the constants used for the calculations are the ideal sizes of the element's css properties for maxWidth

      let baseWidth = this.$el.offsetWidth > 1000 ? this.$el.offsetWidth : 1000 
      //different behaviour for mobile
      if (this.$el.offsetWidth < 440){
        baseWidth = this.$el.offsetWidth > 700 ? this.$el.offsetWidth : 700 
      }        

      let maxWidth = 1360
      // FONTS
      this.fonts.bottom_text = (21 * baseWidth) / maxWidth 
      this.fonts.top_text = (35 * baseWidth) / maxWidth
      this.fonts.middle_text = (25 * baseWidth) / maxWidth 

      // Paddings used for circle size
      this.circle_dimensions.padding_top = (25 * baseWidth) / maxWidth
      this.circle_dimensions.padding_left = (35 * baseWidth) / maxWidth
    },
    renderChart() {
      const $this = this,
            chords = this.data,
            t = this.getTransition();

      if(!this.data) return;
      // avoid other transitions while this runs ¬
      t
        .on("start",
            () => this._transitioning = true )
        .on("end",
            () => this._transitioning = false );

      const fms = this.chart.select("g.fms")
                      .selectAll("g.item")
                      .data(chords.sources),
            beneficiaries = this.chart.select("g.beneficiaries")
                      .selectAll("g.item")
                      .data(chords.targets),
            links = this.chart.select("g.links")
                      .selectAll("path")
                      .data(chords);

      const fmcolour = (d) => this.FM_ARRAY[d.index].colour,

            extract_coords = (d) => ({
              startAngle: d.startAngle,
              endAngle: d.endAngle,
            }),
            extract_link_coords = (d) => ({
              source: extract_coords(d.source),
              target: extract_coords(d.target),
            }),

            txtTransform = (d, direction) => `rotate(${(
              (d.startAngle + d.endAngle) / 2
              / Math.PI * 180
              - 90 * direction
            )})`;

      function mktweener(tweenfunc, coordsfunc) {
        return function(d) {
          const interpolate = d3.interpolate(
            this._prev, coordsfunc(d)
          );
          this._prev = interpolate(0);

          return function(x) {
            return tweenfunc(interpolate(x));
          }
        }
      }

      const fentered = fms.enter()
        .append("g")
        .style("fill", fmcolour)
        .style("stroke", fmcolour);

      const bentered = beneficiaries.enter()
        .append("g");

      const _options = {
        source: {
          items: this.FM_ARRAY,
          filterfunc: this.toggleFm,
          direction: -1,
        },
        target: {
          items: this.BENEFICIARY_ARRAY,
          filterfunc: this.toggleBeneficiary,
          direction: 1,
        }
      };

      const setUp = (sel, type) => {
        const opts = _options[type];
        const item = (i) => opts.items[i];

        sel
          .attr("class", (d, i) => "item " + item(i).id )
          .on("click", (d, i) => opts.filterfunc(item(i)) )
          .on("mouseenter", this.mkhighlight(type))
          .on("mouseleave", this.mkunhighlight(type));

        const arc = sel
          .append("path")
          .attr("class", "arc")
          .each(function(d) {
            this._prev = extract_coords(d);
          })
          .attr("d", this.arc)
          .attr("stroke-opacity", d => d.value === 0 ? 0 : this[type + "_stroke_opacity"])

        // blank stuff so the area behind the text reacts to mouse events
        const blank = sel
          .append("path")
          .attr("class", "blank")
          .each(function(d) {
            this._prev = extract_coords(d);
          })
          .attr("d", this.blank);

        const txt = sel
          .append("g")
          .attr("class", "text")
          .attr("transform", (d) => txtTransform(d, opts.direction) )
          .attr("opacity", (d) => d.value == 0 ? 0 : 1 )
          .call(itemText, type);
      };

      const _textProps = (sel, opts) => {
        sel
          .attr("x", this.radius * opts.direction )
          .attr("dx", this.textPadding * opts.direction)
          .attr("dy", ".33em");
      }

      const itemText = (sel, type) => {
        const opts = _options[type];

        if (type == "target") {
          sel
            .append("text")
            .text( (d, i) => opts.items[i].name )
            .call(_textProps, opts);

          return;
        }

        sel
          .filter( (d, i) => opts.items[i].id == "norway-grants" )
          .append("text")
          .text("Norway")
          .call(_textProps, opts);

        sel
          .filter( (d, i) => opts.items[i].id == "eea-grants" )
          .selectAll("text").data(
            ["Iceland", "Liechtenstein", "Norway"]
          )
          .enter()
          .append("text")
          .attr("transform", (d, i, data) => `rotate(${
            this.textDegrees * this.text_spacing
            * (i - (data.length - 1) / 2) * opts.direction
          })` )
          .text( (d) => d )
          .call(_textProps, opts);
      }

      fentered.call(setUp, "source");
      bentered.call(setUp, "target");

      const _objs = {
        source: fms,
        target: beneficiaries,
      }

      for (const type in _objs) {
        const sel = _objs[type]

        sel.select("path.arc")
          .transition(t)
          .attrTween('d', mktweener(this.arc, extract_coords))
          // show / hide the items at the beginning / end of transitions
          // (because even if 0-width their stroke keeps them visible)
          .attr("stroke-opacity", d => d.value === 0 ? 0 : this[type + "_stroke_opacity"])
          .on("start", function(d) {
            if (d.value != 0) d3.select(this).style("display", null)
          })
          .on("end", function(d) {
            if (d.value == 0) d3.select(this).style("display", "none")
          })

        sel.select("path.blank")
          // don't tween this, save some cpu cycles
          //.transition(t)
          //.attrTween('d', mktweener(this.blank, extract_coords));
          .attr('d', this.blank);

        sel.select("g.text")
          .transition(t)
          .attr("transform", (d) => txtTransform(d, sel === fms ? -1 : 1) )
          .attr("opacity", (d) => d.value == 0 ? 0 : 1);
      }

      links.enter()
        .append("path")
        .on("mouseenter", this.highlight)
        .on("mouseleave", this.unhighlight)
        .each(function(d) {
          this._prev = extract_link_coords(d);
        })
        .attr("d", this.link);

      links
        .transition(t)
        .attrTween('d', mktweener(this.link, extract_link_coords));
    },

    _highlight(index, yes) {
      //// avoid funny race conditions ¬
      // (to be enabled if mouse-over gets transitioned)
      //if(this._transitioning) return;

      //const t = this.getTransition(this.short_duration);

      const links = this.chart.select("g.links").selectAll("path");

      links.filter( (d, i) => i == index )
           .classed("highlighted", yes);
      links.filter( (d, i) => i != index)
           .classed("non-highlighted", yes);
    },

    _grouphighlight(index, type, yes) {
      //// avoid funny race conditions ¬
      //if(this._transitioning) return;

      //const t = this.getTransition(this.short_duration);

      const links = this.chart.select("g.links").selectAll("path");

      links.filter( (d) => d[type].index == index )
           .classed("highlighted", yes);
      links.filter( (d) => d[type].index != index )
           .classed("non-highlighted", yes);
    },

    highlight(d, i) {
      this._highlight(i, true);
    },

    unhighlight(d, i) {
      this._highlight(i, false);
    },

    mkhighlight(type) {
      const $this = this;
      return function(d, i) {
        $this._grouphighlight(i, type, true);
      };
    },

    mkunhighlight(type) {
      const $this = this;
      return function(d, i) {
        $this._grouphighlight(i, type, false);
      };
    }
  },
});
</script>
