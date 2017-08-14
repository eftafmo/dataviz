<style lang="less">
.viz.map.projects {
  .chart {
    .states > .beneficiary,
    .regions > .state > g.layer > g {
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
  type: "projects",

  mixins: [
    ProjectsMixin,
  ],

  data() {
    return {
      // need to set these so pointer events work in IE
      beneficiary_colour_default: "#fff",
      region_colour_default: "#fff",
      title: 'Projects Map'
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

      let details = `
        <li>${ this.number(num_projects) } ` + this.singularize(`projects`, num_projects) + `</li>
      `;
      if (num_projects) {
        details += `
          <li>${ this.currency(d.allocation || 0) }</li>
          <li>${d.sectors.size()} `+  this.singularize(`sectors`, d.sectors.size()) + `</li>
          <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
          <li>${d.programmes.size() ? d.programmes.size() + " " + this.singularize(`programmes`, d.programmes.size()) : "TODO: programme count"}</li>
        `;
      }

      if (d.id.length == 2) {
        return `
          <div class="title-container">
            <svg>
              <use xlink:href="#${this.get_flag_name(d.id)}" />
            </svg>
            <span class="name">${ this.COUNTRIES[d.id].name }</span>
          </div>
          <ul>
            ${ details }
          </ul>
        `;
      } else {
        return `
          <div class="title-container">
            <svg>
              <use xlink:href="#${this.get_flag_name(d.id)}" />
            </svg>
            <span class="name">${ this.get_nuts_label(d.id) } (${d.id})</span>
          </div>
          <ul>
            ${ details }
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
        x: this.map.geodetails[d.id].centroid.x,
        y: this.map.geodetails[d.id].centroid.y,
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

    _mkLevelData(regiondata) {
      // re-aggregate the data to compute per-level stuff
      const leveldata = {};
      this.draw_nuts_levels.forEach(x => leveldata[x] = {});

      for (const row of regiondata) {
        const root = row.id.substring(0, 2),
              code = row.id.substr(2),
              maxlevel = code.length;

        for (let lvl = 1; lvl <= maxlevel; lvl++) {
          const nuts = root + code.substring(0, lvl);

          let item = leveldata[lvl][nuts];
          if (item === undefined) {
            item = leveldata[lvl][nuts] = {};

            for (const k in row) {
              // can't simply Object.assign, because of sets
              const v = row[k];

              if (v instanceof d3.set)
                item[k] = d3.set(v.values());
              else
                item[k] = v;

              // overwrite id
              item.id = nuts;
            }
          } else {
            for (const k in row) {
              const v = row[k];

              if (typeof v == 'string')
                continue;
              else if (typeof v == 'number')
                item[k] += v;
              else if (v instanceof d3.set)
                v.each(x => item[k].add(x));
              else
                console.error("Unhandled key / value", k, v);
            }
          }
        }
      }

      // flatten
      const out = [];
      for (const lvl in leveldata) {
        const regions = leveldata[lvl],
              row = {
                level: lvl,
                regions: [],
              };

        out.push(row);

        for (const r in regions) {
          row.regions.push(regions[r]);
        }
      }

      return out;
    },

    renderRegionData(state, regiondata, t) {
      if (t === undefined) t = this.getTransition();

      const dataset = this._mkLevelData(regiondata);

      let regions = this.chart
        .select(`.regions > .state.${state}`)
        .selectAll("g.layer")
        .data(dataset, d => d.level)
        .selectAll("g.region");

      regions.filter( (d) => (d.type == "Feature" ) )
             .call(this._mkProjectCircles,
                   this.map.geodetails[state].transform.k);

      regions = regions.data(
          d => d.regions,
          d => d.id
        );

      regions.select("g")
        .call(this._updateProjects, t);

      regions.exit().merge(regions.filter( (d) => d.project_count == 0 ))
        .select("g") // circle
        // hack to "set" the data to 0 (for the tooltip anyway)
        .each(d => d.project_count = 0)
        .call(this._updateProjects, t)

        .transition(t)
        .attr("opacity", 0);
    },

    handleFilterBeneficiary(newid, oldid) {
      this.$super.handleFilterBeneficiary(newid, oldid);

      // hide the big circles, they're distractive
      const t = this.getTransition();
      this.chart.selectAll('g.states > g.beneficiary > g')
        .transition(t)
        .attr("opacity", Number(!newid));
    },
  },
});
</script>
