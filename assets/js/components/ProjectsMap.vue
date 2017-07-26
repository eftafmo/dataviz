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
    textDimensions() {
      // compute the dimensions of an average number character
      if (!this.isReady) return 0;

      // respect where the text will appear so css applies properly
      const fakeB = this.chart.select(".states")
                        .append("g")
                        .attr("class", "beneficiary");
      const txt = fakeB.append("text")
                       .attr("visibility", "hidden")
                       .text("1234567890");

      const bounds = txt.node().getBBox();
      fakeB.remove();

      return {width: bounds.width / 10, height: bounds.height};
    },
  },

  methods: {
    tooltipTemplate(d) {
      const allocation = d.allocation || 0;
      const num_projects = this.get_project_count(d);

      if (d.id.length == 2) {
        let extra = "";
        if (num_projects) {
          extra = `
            <li>${ this.currency(d.allocation || 0) }</li>
            <li>${d.sectors.size()} `+  this.singularize(`sectors`, d.sectors.size()) + `</li>
            <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
            <li>${d.programmes.size()}  `+  this.singularize(`programmes`, d.programmes.size()) + `</li>
          `;
        }

        return `
          <div class="title-container">
          <svg>
            <use xlink:href="#${this.get_flag_name(d.id)}" />
          </svg>
            <span class="name">${ this.COUNTRIES[d.id].name }</span>
          </div>
          <ul>
            <li>${ this.number(num_projects) } ` + this.singularize(`projects`, num_projects) + `</li>
            ${ extra }
          </ul>
        `;
      } else {
        return `
          <div class="title-container">
            <span class="name">${ this.region_names[d.id] } (${d.id})</span>
          </div>
          <ul>
            <li>${ num_projects } ` + this.singularize(`projects`, num_projects) + `</li>
            <li>TODO: number of sectors, programme areas, programmes</li>
          </ul>
        `;
      }
    },

    get_project_count(d) {
      return d.project_count || 0;
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
      const dataset = d3.values(this.data);

      let beneficiaries = this.chart.selectAll('.states > g.beneficiary');

      // do an initial render of the circles,
      // (because we never have an enter selection for beneficiaries)
      beneficiaries.filter( (d) => (d.type == "Feature" ) )
                   .call(this._mkProjectCircles)

      // only now bind the data
      beneficiaries = beneficiaries.data(dataset, (d) => d.id );

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
          let len;
          return (
            count == 0 ? this.textDimensions.width / 3 : (
              (len = count.toString().length) == 1 ?
              this.textDimensions.height :
              (len + 1/2) * this.textDimensions.width
            ) / 2 * 1.3 // a lil' bit of extra
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
