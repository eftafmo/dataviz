<template>
<div class="overview-viz">
  <svg :width="width" :height="height">
    <!-- with a bit of hardcoded rotation, because -->
    <g class="chart" :transform="`rotate(-3.5),translate(${width/2},${height/2})`" />
  </svg>
</div>
</template>


<style lang="less">
.overview-viz {
  .chart {
    path.chord {
      fill: #ccc;
      /*fill-opacity: .8;*/
    }
  }
}
</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';

import stretchedChord from 'js/lib/d3.stretched.chord';
import customChordLayout from 'js/lib/d3.layout.chord.sort';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import CSVReadingMixin from './mixins/CSVReading';
import WithFMsMixin from './mixins/WithFMs';
//import WithCountriesMixin from './mixins/WithCountries';


export default Vue.extend({
  mixins: [
    BaseMixin, CSVReadingMixin,
    ChartMixin, WithFMsMixin, //WithCountriesMixin,
  ],

  props: {
    width: Number,
    height: Number,
    pullOut: {
      type: Number,
      default: 30,
    },
    emptyPerc: {
      type: Number,
      default: 0.7, // "percenteage" of circle that becomes empty
    },
  },

  data() {
    return {
    };
  },

  computed: {
    data() {
      // the chord layout needs a matrix as input
      const from_ = this.dataset.columns.slice(2), // skips id & name
            to_ = this.dataset.map( (d) => d.name ); // d.id?

      // items are in fact a circle, starting clockwise with first country,
      // then a dummy item, then the financial mechanisms bottom to top,
      from_.reverse();
      // end ending with another dummy item
      const names = [].concat(to_, [""], from_, [""]);

      let total = 0;

      const to_matrix = this.dataset.map( (row) => {
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

      const getColour = (d,i) => {
        if (names[i] === "") return "none";
        const fmcolour = this.colour(names[i]);
        return fmcolour ? fmcolour : "#ccc";
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
