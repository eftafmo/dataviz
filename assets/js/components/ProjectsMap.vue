<style lang="less">
.map-viz {
  .chart {
    .states > .beneficiary,
    .regions > .state > g {
      & > g {
        pointer-events: none;

        circle {
          fill: rgb(196, 17, 48);
          fill-opacity: .4;
          transform-origin: 50% 50%;
        }

        text {
          font-size: 1.2em;
          font-family: 'Open sans', sans-serif;
          font-weight: 600;
          text-anchor: middle;
          fill: #fff;
        }
      }

      &:hover > g circle {
        fill-opacity: .7;
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

  data() {
    return {
      beneficiary_colour_default: '#fff',
    };
  },

  computed: {
    numberWidth() {
      // compute the length of an average number character
      // as it will appear for project counts
      if (!this.isReady) return 0;

      // respect where the text will appear so css applies properly
      const fakeB = this.chart.select(".states")
                        .append("g")
                        .attr("class", "beneficiary");
      const txt = fakeB.append("text")
                       .attr("visibility", "hidden")
                       .text("1234567890");

      const bbox = txt.node().getBBox(),
            txtwidth = (bbox.width / 10 + bbox.height) / 2;
      fakeB.remove();

      // return one character's width with some safety extra
      return txtwidth;
    },
  },

  methods: {
    tooltipTemplate(d) {
      if (d.id.length == 2)
        return `
          <div class="title-container">
            <img src="/assets/imgs/${ this.get_flag_name(d.id) }.png" />
            <span class="name">${ this.COUNTRIES[d.id].name }</span>
          </div>
          <ul>
            <li>${ this.number(this.get_project_count(d)) } projects</li>
            <li>${ this.currency(d.total || 0) } gross allocation</li>
          </ul>
        `;
      else
        return `
          <div class="title-container">
            <span class="name">${ this.region_names[d.id] } (${d.id})</span>
          </div>
          <ul>
            <li>${ this.number(this.get_project_count(d)) } projects</li>
            <li>${ this.currency(d.allocation || 0) } gross allocation</li>
          </ul>
          <small>(Temporary)<small>
        `;
    },

    get_project_count(d) {
      // the project count is split among fms (which is probably useless)
      return (
        typeof d.project_count === 'number' ?
          d.project_count :
          d3.sum(d3.values(d.project_count)) || 0
      );
    },

    _mkProjectCircles(sel, k) {
      const container = sel.append("g")
                           .attr("opacity", 1);

      const _c = (d) => ({
        x: this.geodetails[d.id].centroid[0],
        y: this.geodetails[d.id].centroid[1]
      });

      container
        .append("circle")
        .attr("cx", (d) => _c(d).x )
        .attr("cy", (d) => _c(d).y );

      container
        .append("text")
        .attr("x", (d) => _c(d).x )
        .attr("y", (d) => _c(d).y )
        .attr("dy", ".33em"); // magical self-centering offset

      if (k)
        container.attr("transform", (d) => (
          `translate(${_c(d).x * (1 - 1/k)}, ${_c(d).y * (1 - 1/k)}) scale(${1/k})`
        ) );
    },

    renderData(t) {
      if (t === undefined) t = this.getTransition();

      const beneficiarydata = d3.values(this.beneficiarydata);
      let beneficiaries = this.chart.selectAll('.states > g.beneficiary');

      // do an initial render of the circles,
      // (because we never have an enter selection for beneficiaries)
      beneficiaries.filter( (d) => (d.type == "Feature" ) )
                   .call(this._mkProjectCircles)

      // only now bind the data
      beneficiaries = beneficiaries.data(beneficiarydata, (d) => d.id );

      const projects = beneficiaries
        .filter( (d) => d.id !== this.filters.beneficiary )
        .select("g");

      projects
        .transition(t)
        .attr("opacity", 1);

      beneficiaries
        .filter( (d) => d.id == this.filters.beneficiary )
        .select("g")
        .transition(t)
        .attr("opacity", 0);

      beneficiaries.exit().select("g")
        .transition(t)
        .attr("opacity", 0);

      projects.call(this._updateProjects, t);
    },

    _updateProjects(sel, t) {
      const $this = this;

      sel
        .transition(t)
        .attr("opacity", 1);

      // the circle radius is only meant to fit the text,
      // not show some smart correlation :)
      sel.select("circle")
        .transition(t)
        .attr("r", (d) => {
          const count = this.get_project_count(d);
          // return enough for the the text to fit, plus spacing
          // for another half a character, but not if zero
          return (
            count == 0 ?
            this.numberWidth / 3 :
            (count.toString().length + 1/2) * this.numberWidth / 2
          );
        } );

      sel.select("text")
        .filter(function(d) {
          return this.textContent != $this.get_project_count(d);
        })
        .each(function() {
          // clone the old text and fade it out
          const clone = d3.select(
            this.parentNode.appendChild(this.cloneNode(true))
          );
          clone
            .attr("opacity", 1)
            .transition(t)
            .attr("opacity", 0)
            .on("end", function() {
              clone.remove();
            })
        })
        // while the real thing gets faded back in
        .attr("opacity", 0)
        .text((d) => {
          const count = this.get_project_count(d);
          return count == 0 ? "" : count
        } )
        .transition(t)
        .attr("opacity", 1);
    },

    _renderRegionData(state, regiondata, t) {
      if (t === undefined) t = this.getTransition();

      // repeat hacky pre-draw-circle and post-bind-data, meh
      let regions = this.chart.selectAll(`.regions > .state.${state} > g`);

      regions.filter( (d) => (d.type == "Feature" ) )
             .call(this._mkProjectCircles, this.zoomLevel);

      regions = regions.data(regiondata, (d) => d.id );

      regions.select("g")
        .call(this._updateProjects, t);

      regions.exit().merge(regions.filter( (d) => d.project_count == 0 ))
        .select("g")
        .transition(t)
        .attr("opacity", 0);
    },
  },
});
</script>
