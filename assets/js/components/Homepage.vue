<template>
<div class="overview-viz">
  <chart-container :width="width" :height="height">
    <svg :viewBox="`0 0 ${width} ${height}`">
      <!-- with a bit of hardcoded rotation, because -->
      <g class="chart" :transform="`rotate(-3.5),translate(${width/2},${height/2})`" />
    </svg>

    <div v-if="hasData" class="info">
      <transition name="fade"><div class="heading" :key="changed">
        <p><span class="amount">{{ currency(aggregated.allocation) }}</span> spent on</p>
      </div></transition>
      <div class="data-wrapper"><transition name="fade"><ul class="data" :key="changed">
        <li class="programmes"><span class="amount">{{ number(aggregated.programmes.size()) }}</span> Programmes</li>
        <li class="projects"><span class="amount">{{ number(aggregated.project_count) }}</span> Projects</li>
      </ul></transition></div>
      <div class="ending">
        <p>to reduce social and economic disparities across Europe and to strenghten bilateral relations</p>
      </div>
    </div>

    <fm-legend :fms="FMS" class="legend clearfix">
      <template slot="fm-content" scope="x">
        <span :style="{backgroundColor: x.fm.colour}"></span>
        {{ x.fm.name }}
      </template>
    </fm-legend>
  </chart-container>
</div>
</template>


<style lang="less">
.overview-viz {
  .chart {
    g.group {
      cursor: pointer;
    }

    path.chord {
      fill: #ccc;
      /*fill-opacity: .8;*/
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

      font-size: 1.5em;

      /*
      .amount {
        font-size: 1.2em;
      }
      */
    }

    .data-wrapper {
      width: 40%;
      padding-bottom: 40%;
      left: 30%;
      top: 30%;
      //background-color: rgba(251, 251, 251, 0.8);
      background-image: linear-gradient(rgba(252, 252, 252, .75), rgba(227, 227, 227, .95));
      border: .2em solid white;
      border-radius: 50%;
    }

    .data {
      list-style-type: none;
      padding: 0;

      position: absolute;
      width: 100%;
      left: 50%;
      top: 50%;
      transform: translate(-50%,-50%);

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
    }
  }

  .legend {
    position: absolute;
    left: 0;
    top: 0;

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
    @media (min-width: 800px)and (max-width:1000px){
      width: 84%;
    }
    @media (min-width:1000px) {
      width: 60%;
    }
  }
}
</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';
import {slugify} from 'js/lib/util';

import stretchedChord from 'js/lib/d3.stretched.chord';
import customChordLayout from 'js/lib/d3.layout.chord.sort';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithFMsMixin, WithCountriesMixin
  ],

  props: {
    width: Number,
    height: Number,
  },

  data() {
    return {
      pullOut: 30,
      beneficiary_colour: "#ccc",
      emptyPerc: 0.7, // "percentage" of circle that becomes empty
    };
  },

  computed: {
    filtered() {
      return this.filter(this.dataset);
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
      const $this=this;
      const _dataset = {};
      const fmnames = d3.values(this.FMS).map( (fm) => fm.name ),
            _fmsobj = {};
      fmnames.forEach( (n) => _fmsobj[n] = 0 );

      for (const d of this.dataset) {
        const value = +d.allocation,
              b = d.beneficiary;
        if (value == 0) continue;

        let beneficiary = _dataset[b];
        if (beneficiary === undefined)
          beneficiary = _dataset[b] = Object.assign(
            { name: this.COUNTRIES[b].name },
            _fmsobj
          )
        beneficiary[d.fm] += value;
      }
      const dataset = d3.values(_dataset);
      dataset.sort((a, b) => a.name.charCodeAt(0) - b.name.charCodeAt(0));


      // the chord layout needs a matrix as input
      const from_ = fmnames,
            to_ = dataset.map( (d) => d.name );

      // items are in fact a circle, starting clockwise with first country,
      // then a dummy item, then the financial mechanisms bottom to top,
      from_.reverse();
      // end ending with another dummy item
      const names = [].concat(to_, [""], from_, [""]);

      let total = 0;

      const to_matrix = dataset.map( (row) => {
        return from_.map( (f) => {
          const val = +row[f];
          // we take this wonderful opportunity for some side-effects
          total += val;
          return val;
        });
      });

      const from_matrix = d3.transpose(to_matrix);

      // we're gonna use these to fill the matrix rows
      const from_zeros = new Array(from_.length).fill(0),
            to_zeros = new Array(to_.length).fill(0);


      const build_to = (row, _i, _arr, dummy) => [].concat(
              to_zeros, [0], row, dummy ? [dummy] : [0]
            ),
            build_from = (row, _i, _arr, dummy) => [].concat(
              row, dummy ? [dummy] : [0], from_zeros, [0]
            );

      const _empty = Math.round(total * this.emptyPerc);

      const matrix = [].concat(
        to_matrix.map(build_to),
        // bottom dummy
        [build_to(from_zeros, null, null, _empty)],

        from_matrix.map(build_from),
        // top dummy
        [build_from(to_zeros, null, null, _empty)]
      );
      return {
        names,
        matrix,
        total,
        _empty,
      };
    },
  },

  methods: {
    renderChart() {
      var data = this.data,
          names = data.names,
          matrix = data.matrix,
          total = data.total,
          _empty = data._empty;

      var width = this.width,
          height = this.height;

      var outerRadius = Math.min(width, height) / 2 * 0.8,
          innerRadius = outerRadius * 0.85,
          pullOutSize = this.pullOut,
          emptyPerc = this.emptyPerc,
          opacityDefault = 0.7, // default opacity of chords
          opacityLow = 0 // opacity of non-hovered chords

          //Calculate how far the Chord Diagram needs to be rotated clockwise to make the dummy
          //invisible chord center vertically
      var offset = (2 * Math.PI) * (
        _empty / (total + _empty)
      ) / 4;




////////////////////////////////////////////////////////////
////////////////// Extra Functions /////////////////////////
////////////////////////////////////////////////////////////

//Include the offset in de start and end angle to rotate the Chord diagram clockwise
const startAngle= (d) => d.startAngle + offset;
const endAngle = (d) => d.endAngle + offset;

// Returns an event handler for fading a given chord group
const fade = (opacity) => {
  return (d, i) => {
  this.chart.selectAll("path.chord")
    .filter(function(d) { return d.source.index !== i && d.target.index !== i && names[d.source.index] !== ""; })
    .transition()
    .style("opacity", opacity);
  };
}//fade

// Fade function when hovering over chord
const fadeOnChord = (d) => {
  var chosen = d;
  this.chart.selectAll("path.chord")
    .transition()
    .style("opacity", function(d) {
      return d.source.index === chosen.source.index && d.target.index === chosen.target.index ? opacityDefault : opacityLow;
    });
}//fadeOnChord

      const getColour = (d, i) => {
        const name = names[i];
        if (name === "") return "none";

        const fm = this.FMS[slugify(name)]
        if (fm === undefined) return this.beneficiary_colour;

        return fm.colour;
      };

////////////////////////////////////////////////////////////
///////////////////////// init /////////////////////////////
////////////////////////////////////////////////////////////

//Custom sort function of the chords to keep them in the original order
var chord = customChordLayout() //d3.layout.chord()
  .padding(.02)
  .sortChords(d3.descending) //which chord should be shown on top when chords cross. Now the biggest chord is at the bottom
  .matrix(matrix);

var arc = d3.arc()
  .innerRadius(innerRadius)
  .outerRadius(outerRadius)
  .startAngle(startAngle) //startAngle and endAngle now include the offset in degrees
  .endAngle(endAngle);


var path = stretchedChord() //Call the stretched chord function
  .radius(innerRadius)
  .startAngle(startAngle)
  .endAngle(endAngle)
  .pullOutSize(pullOutSize);

////////////////////////////////////////////////////////////
//////////////////// Draw outer Arcs ///////////////////////
////////////////////////////////////////////////////////////

var g = this.chart.selectAll("g.group")
  .data(chord.groups)
  .enter().append("g")
  .attr("class", "group")
  .on("mouseover", fade(opacityLow))
  .on("mouseout", fade(opacityDefault))
  .on("click", (d, i) => {
    const name = names[i];
    if (name === "") return;

    const fm = this.FMS[slugify(name)]
    if (fm !== undefined) {
      this.toggleFm(fm);
      return;
    }

    const beneficiary = d3.values(this.BENEFICIARIES).find(
      (x) => x.name == name
    );

    this.toggleBeneficiary(beneficiary);
  } )


g.append("path")
  .style("stroke", getColour)
  .style("fill", getColour)
  .style("pointer-events", function(d,i) { return (names[i] === "" ? "none" : "auto"); })
  .attr("d", arc)
  .attr("transform", function(d, i) { //Pull the two slices apart
        d.pullOutSize = pullOutSize * ( d.startAngle + 0.001 > Math.PI ? -1 : 1);
        return "translate(" + d.pullOutSize + ',' + 0 + ")";
  });

////////////////////////////////////////////////////////////
////////////////////// Append Names ////////////////////////
////////////////////////////////////////////////////////////

//The text also needs to be displaced in the horizontal directions
//And also rotated with the offset in the clockwise direction
g.append("text")
  .each(function(d) { d.angle = ((d.startAngle + d.endAngle) / 2) + offset;})
  .attr("dy", ".35em")
  .attr("class", "titles")
  .style("font-size", "10px" )
  .attr("text-anchor", function(d) { return d.angle > Math.PI ? "end" : null; })
  .attr("transform", function(d,i) {
    var c = arc.centroid(d);
    return "translate(" + (c[0] + d.pullOutSize) + "," + c[1] + ")"
    + "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
    + "translate(" + 20 + ",0)"
    + (d.angle > Math.PI ? "rotate(180)" : "")
  })
  .text(function(d,i) { return names[i]; });

////////////////////////////////////////////////////////////
//////////////////// Draw inner chords /////////////////////
////////////////////////////////////////////////////////////

this.chart.selectAll("path.chord")
  .data(chord.chords)
  .enter().append("path")
  .attr("class", "chord")
  .style("stroke", "none")
  .style("opacity", function(d) { return (names[d.source.index] === "" ? 0 : opacityDefault); }) //Make the dummy strokes have a zero opacity (invisible)
  .style("pointer-events", function(d,i) { return (names[d.source.index] === "" ? "none" : "auto"); }) //Remove pointer events from dummy strokes
  .attr("d", path)
  .on("mouseover", fadeOnChord)
  .on("mouseout", fade(opacityDefault));
    },
  },
});
</script>
