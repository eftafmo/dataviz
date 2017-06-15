<template>
<div class="overview-viz">
<div v-if="isReady" class="circle-wrapper">
    <div class="circle">
      <div class="programmes-count"><span>{{data.programmes_total}}</span><br>Programmes</div>
      <div class="projects-count"><span>{{data.projects_total}}</span><br>Projects</div>
    </div>
    <div class="line-wrapper">
      <div class="donor-count"><span>3</span> Donor states</div>
      <div class="states-count"><span>{{data.beneficiary_count}}</span> Beneficiary states</div>
  </div>
 </div>
  <div v-if="hasData" class="legend">
    <fm-legend :fms="FMS" class="clearfix">
      <template slot="fm-content" scope="x">
        <span :style="{backgroundColor: x.fm.colour}"></span>
        {{ x.fm.name }}
      </template>
    </fm-legend>
  </div>
  <chart-container :width="width" :height="height">
    <svg :viewBox="`0 0 ${width} ${height}`">
      <!-- with a bit of hardcoded rotation, because -->
      <g class="chart" :transform="`rotate(-3.5),translate(${width/2},${height/2})`" />
    </svg>
  </chart-container>
  <div class="total-spent"><h1 v-if="isReady">{{format(data.total)}}</h1>
    <h3>spent on</h3>
  </div>
  <div class="overview-info">to reduce social and economic disparities across europe and to strenghten bilateral relations</div>
</div>
</template>


<style lang="less">
.overview-viz {
  .chart {
    position: relative;
    path.chord {
      fill: #ccc;
      /*fill-opacity: .8;*/
    }
  }

  .donor-count, .states-count {
    word-spacing: 30rem;
    text-align: center;
    max-width: 150px;
    span {
      font-weight: bold;
    }
    font-size: 1.7rem;
  }


  .donor-count {
    margin-left: 15%;
  }

  .states-count {
    margin-right: 8%;
  }

  .line-wrapper {
    display: flex;
    justify-content: space-between;
    position: absolute;
    top: 40%;
    width: 100%;
  }

  .total-spent {
    position: absolute;
    top: 1rem;
    left: 45%;
    text-align: center;
  }

  .overview-info {
    position: absolute;
    left: 38%;
    text-align: center;
    max-width: 350px;
    font-size: 2rem;
    bottom: 9%;
  }

  .circle-wrapper {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: absolute;
    top: 0;
    font-size: 3rem;
    text-align: center;
    span {
      font-weight: bold;
      font-size: 4.5rem;
    }
    .circle {
      background: rgba(251, 251, 251, 0.86);
      padding: 6rem 7rem;
      border-radius: 100rem;
      border: 4px solid white;
      margin-left: 5rem;
      margin-top: 2rem;
      z-index: 1;
    }
  }

  .legend {
    cursor: pointer;
    position: relative;
    z-index: 1;
    .fm span {
      width: 10px; height: 10px;
      display: inline-block;
    }
    li {
      list-style-type: none;
      display: inline-block;
      margin-right: 2rem;
    }
    .fm {
      transition: all .5s ease;
      display: block;
    }
    .fm.disabled {
      filter: grayscale(100%);
      opacity: 0.5;
    }

    .fm.selected {
      text-shadow: 0 0 1px #999;
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
import {mydata} from './dummy.js'


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
    data() {
      this.dataset = mydata
      const $this=this;
      const _dataset = {};
      const fmnames = d3.values(this.FMS).map( (fm) => fm.name ),
            _fmsobj = {};
      fmnames.forEach( (n) => _fmsobj[n] = 0 );

      for (const d of this.dataset) {
        const value = +d.allocation,
              b = d.beneficiary,
              project_count = d.project_count,
              programmes_list = d.programmes;
        if (value == 0) continue;

        let beneficiary = _dataset[b];
        if (beneficiary === undefined)
          beneficiary = _dataset[b] = Object.assign(
            { name: this.COUNTRIES[b].name },
            _fmsobj,
            { project_count: project_count },
            { programmes : []},
            { programmes_count : 0}
          )
        beneficiary[d.fm] += value;
      }
      const dataset = d3.values(_dataset);
      dataset.sort((a, b) => a.name.charCodeAt(0) - b.name.charCodeAt(0));

      let dup = []
      let programmes_total = 0;
      let projects_total = 0;
      for (const d of dataset) {
        for (const c of this.dataset ) {
          if(this.COUNTRIES[c.beneficiary].name == d.name)
          {d.programmes.push(c.programmes)}
        }
        for (let a of d.programmes) {
            for (let c of a) {
              dup.push(c);
            }
        }
        projects_total += d.project_count
       }
      let unique = dup.filter(function(elem, index, self) {
            return index == self.indexOf(elem);
      })
      programmes_total = unique.length


      console.log(dataset)
      // the chord layout needs a matrix as input
      const from_ = fmnames,
            to_ = dataset.map( (d) => d.name );

      const beneficiary_count = to_.length;
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
        beneficiary_count,
        programmes_total,
        projects_total,
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
  .on("mouseout", fade(opacityDefault));



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
