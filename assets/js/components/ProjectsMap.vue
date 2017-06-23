<style lang="less">
.map-viz {
  .chart {
    .data {
      // temporary hack until this stuff gets grouped with the country path
      pointer-events: none;

      circle {
        fill: rgb(196, 17, 48);
        fill-opacity: .4;
        transform-origin: 50% 50%;
      }
      circle:hover {
        transform: scale(1.2, 1.2)
      }

      text {
        font-size: 1.2em;
        font-family: 'Open sans', sans-serif;
        font-weight: 600;
        text-anchor: middle;
        fill: #fff;
      }
    }
  }
}
</style>

<script>
import * as d3 from 'd3';

import BaseMap from './BaseMap';
import ProjectsMixin from './mixins/Projects';


export default BaseMap.extend({
  mixins: [
    ProjectsMixin,
  ],

  computed: {
    numberWidth() {
      // compute the length of an average number character
      // as it will appear for project counts
      if (!this.isReady) return 0;

      // TODO: should this ever get recomputed?

      // respect where the text will appear so css applies properly
      const fakeG = this.chart.select(".data").append("g");
      const txt = fakeG.append("text")
                       .attr("visibility", "hidden")
                       .text("1234567890");

      const txtwidth = txt.node().getBBox().width;
      fakeG.remove();

      // return one character's width with some safety extra
      return txtwidth / 10 * 1.1;
    },
  },

  methods: {
    renderData() {
      const beneficiarydata = d3.values(this.beneficiarydata);

      const projects = this.chart.select(".data").selectAll("g")
                           .data(beneficiarydata, (d) => d.id );

      const pentered = projects.enter().append("g");

      const circles = pentered.append("circle")
        .attr("cx", (d) => this.geodetails[d.id].centroid[0] )
        .attr("cy", (d) => this.geodetails[d.id].centroid[1] )

      const texts = pentered.append("text")
        .attr("x", (d) => this.geodetails[d.id].centroid[0] )
        .attr("y", (d) => this.geodetails[d.id].centroid[1] )
        .attr("dy", ".33em"); // magical self-centering offset

      // TODO: get rid of the silly Math.pows (when switching to real data) :)

      // the circle radius is only meant to fit the text,
      // not show some smart correlation :)
      projects.select("circle").merge(circles)
        .attr("r", (d) => {
          // return enough for the the text to fit plus spacing...
          // ... for... another half a character
          return (Math.round(d.total / Math.pow(10,6)).toString().length + 1/2) * this.numberWidth / 2;
        } )

      projects.select("text").merge(texts)
        .text( (d) => this.currency(d.total / Math.pow(10,6)) );


    },
  },
});
</script>
