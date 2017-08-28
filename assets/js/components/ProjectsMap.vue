<style lang="less">
.viz.map.projects {
  @bubble_color: rgb(196, 17, 48);

  .bubble {
    circle {
      fill: @bubble_color;
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

  .chart {
    .regions {
      &:not(.zero) {
        cursor: pointer;
      }

      &.zero {
        cursor: not-allowed;
      }
    }

    .projects > g > g {
      pointer-events: none;

      .bubble;

      circle {
        fill-opacity: .4;
      }

      &.hovered circle {
        fill-opacity: 1;
      }
    }
  }

  .current-region {
    rect {
      fill: #fff;
      stroke: #000;
      opacity: .75;
    }

    .bubble;

    text.label {
      font-weight: 400;
      text-anchor: start;
      fill: #000;
    }
  }
}
</style>


<script>
import * as d3 from 'd3';

import BaseMap from './BaseMap';
import ProjectsMixin from './mixins/Projects';


let _PARENT_UID // this is a very ugly hack, but, cutting corners


const RegionDetails = {
  props: {
    region: Object,
  },

  template: `
    <g v-if="region"
       class="current-region"
       transform="translate(50, 50)"
    >
      <rect
        :x="box.x"
        :y="box.y"
        :width="box.width"
        :height="box.height"
      />
      <circle :r="getradius(getprojectcount(region))" />
      <text dy=".33em">{{ getprojectcount(region) }}</text>
      <text class="label"
            :x="getradius(' ' + getprojectcount(region))"
            dy=".33em"
      >{{ label }}</text>
    </g>
  `,

  data() {
    return {
      root_label: "National-level projects",
    }
  },

  computed: {
    label() {
      return this.region.id.length == 2 ? this.root_label
                                        : this.get_nuts_label(this.region)
    },

    box() {
      let label = this.label // unly used for calculations

      // unless the region's name is smaller than the root_label
      if (this.region.id.length !== 2 && label.length < this.root_label)
        label = this.root_label

      return {
        x: -this.getradius("abcd"),
        y: -this.getradius("abcd"),
        width: this.getradius(label) * 2,
        height: this.getradius("abcd") * 2,
      }
    },

    self() {
      let component = this

      while (component._uid != _PARENT_UID) {
        component = component.$parent
      }
      return component
    },
  },

  methods: {
    getprojectcount(d) { return this.self.getprojectcount(d) },
    getradius(txt) { return this.self.getradius(txt) },
  },
}


export default BaseMap.extend({
  type: "projects",

  mixins: [
    ProjectsMixin,
  ],

  components: {
    regionDetails: RegionDetails
  },

  data() {
    return {
      // need to set these so pointer events work in IE
      beneficiary_colour: "#fff",
      region_colour: "#fff",

      zoomed_nuts_level: 2,

      all_nuts_levels: [0, 2, 3],

      region_details_props: {
        current_region: null,
        parent: this,
      },
    };
  },

  computed: {
    textDimensions() {
      // compute the dimensions of an average number character
      if (!this.isReady) return 0;

      // respect where the text will appear so css applies properly
      const fakeB = this.projects
                        .append("g")
      const txt = fakeB.append("text")
                       .attr("visibility", "hidden")
                       .text("1234567890");

      const bounds = txt.node().getBBox();
      fakeB.remove();

      return {width: bounds.width / 10, height: bounds.height};
    },
  },

  created() {
    _PARENT_UID = this._uid

    this._rendered_bubbles = {}
  },

  mounted() {
    this.projects = this.chart.append("g")
                        .attr("class", "projects")
  },

  methods: {
    getradius(txt) {
      // return enough for the the text to fit, plus spacing
      // for another half a character
      const len = txt.toString().length
      return (
        len == 1 ? this.textDimensions.height :
        this.textDimensions.width * (len + 1/2)
      ) / 2 * 1.3 // divided by 2 because radius, and multiplied
      // because a lil' bit of hardcoded extra
    },

    tooltipTemplate(d) {
      const allocation = d.allocation || 0;
      const num_projects = this.getprojectcount(d)

      let details = `
        <li>${ this.number(num_projects) } ` + this.singularize(`projects`, num_projects) + `</li>
      `;
      if (num_projects) {
        details += `
          <li>${ this.currency(allocation) }</li>
          <li>${d.sectors.size()} `+  this.singularize(`sectors`, d.sectors.size()) + `</li>
          <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
          <li>${(d.programmes && d.programmes.size()) ? d.programmes.size() + " " + this.singularize(`programmes`, d.programmes.size()) : "TODO: programme count"}</li>
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

    getprojectcount(d) {
      return d.project_count || 0;
    },

    _domouse(over, d, i, group) {
      const id = d.id,
            level = id.length - 2

      // the real data is not here
      // (but don't bother finding it on mouseout)
      if (over) {
        if (level == 0)
          d = this.aggregated[id]
        else
          d = this.region_data[id]
      }

      const self = this.$super._domouse(over, d, i, group)

      if (!self) return

      const _selector = level != 0 ? "." + id.substr(0, 2) : "",
            selector = `${_selector}.level${level} > g.region.${id}`

      const bubble = this.projects.select(selector)
      if (over) bubble.raise()
      bubble.classed("hovered", over)
    },

    getBubbles(parentid) {
      const main = !parentid
      if (main) parentid = ""

      const level = main ? 0
                         : parentid.length == 2 ? 2 // we skip level1
                                                : parentid.length - 2

      const _selector = main ? "" : "." + parentid,
            selector = `g${_selector}.level${level}`

      if (this._rendered_bubbles[parentid])
        return this.projects.select(selector)

      // else do the initial render of all the bubbles
      const regions = this.chart
        .selectAll(`.regions > ${selector} > path.beneficiary`)
        .data()

      const _classes = [`level${level}`]
      if (!main) _classes.push(parentid.substr(0, 2))

      const parent = this.projects
        .append("g")
        .attr("opacity", 0)
        .attr("class", _classes.join(" "))

      const _c = d => this.map.geodetails[d.id].centroid

      const containers = parent.selectAll("g")
                               .data(regions)
                               .enter().append("g")
                               .attr("class", d => `region ${d.id}`)
                               .attr("opacity", 0)
                               .property("_value", 0)

      if (!main) {
        const k = 1 / this.map.geodetails[parentid].transform.k

        containers.attr("transform", d => (
          `translate(${_c(d).x * (1 - k)},${_c(d).y * (1 - k)}) scale(${k})`
        ))
      }

      containers
        .append("circle")
        .attr("cx", d => _c(d).x)
        .attr("cy", d => _c(d).y)

      containers
        .append("text")
        .attr("x", d => _c(d).x)
        .attr("y", d => _c(d).y)
        .attr("dy", ".33em") // magical self-centering offset

      this._rendered_bubbles[parentid] = true
      return parent
    },

    updateProjects(regions, t) {
      const $this = this

      // since the bubbles always exist, we must simulate enter vs update
      const rupdate = regions.filter(function(d) {
        const oldv = this._value
        return oldv != 0 && $this.getprojectcount(d) != oldv
      })

      const rentered = regions.filter(function(d) {
        const oldv = this._value
        return oldv == 0 && $this.getprojectcount(d) != 0
      })

      const rexit = regions.exit().merge(regions.filter(function(d) {
        const oldv = this._value
        return oldv != 0 && $this.getprojectcount(d) == 0
      }))

      // update gets the circle dimension transitioned
      rupdate.select("circle")
        .transition(t)
        .attr("r", d => this.getradius(this.getprojectcount(d)))

      // and the text swapped in
      rupdate.select("text")
        .each(function() {
          // clone the old text and fade it out
          const clone = d3.select(
            this.parentNode.appendChild(this.cloneNode(true))
          )
          clone
            .attr("opacity", 1)
            .transition(t)
            .attr("opacity", 0)
            .on("end", function() {
              clone.remove()
            })
        })
        // while the real thing gets faded in
        .attr("opacity", 0)
        .text(this.getprojectcount)
        .transition(t)
        .attr("opacity", 1)

      // enter gets faded in
      rentered.select("circle")
        .attr("r", d => this.getradius(this.getprojectcount(d)))

      rentered.select("text")
        .text(this.getprojectcount)

      rentered
        .transition(t)
        .attr("opacity", 1)

      // exit gets faded out
      rexit
        .transition(t)
        .attr("opacity", 0)
        // also clear everything just to be nice
        .on("end", function() {
          const self = d3.select(this)
          self.select("circle")
            .attr("r", null)
          self.select("text")
            .text("")
        })

      // finally,
      regions
        .property("_value", this.getprojectcount)
    },

    _renderRegionData(parentid, dataset, t) {
      if (t === undefined) t = this.getTransition()

      const parent = this.getBubbles(parentid)
      const regions = parent.selectAll("g.region")
        .data(dataset, d => d.id)

      const changed = this._oldparentid !== undefined &&
                      this._oldparentid != parentid

      // if changed don't transition bubble content,
      regions.call(this.updateProjects,
                   changed ? this.getTransition(0) : t)

      if (changed) {
        // but just fade in the main container
        parent
          .style("display", null)
          .transition(t)
          .attr("opacity", 1)

        // (and out the old)
        this.getBubbles(this._oldparentid)
          .classed("transitioning", true)
          .transition(t)
          .attr("opacity", 0)
          .on("end", function() {
            d3.select(this)
              .style("display", "none")
              .classed("transitioning", false)
          })
      }
      else parent.attr("opacity", 1)

      this._oldparentid = parentid
    },

    renderData(t) {
      const dataset = d3.values(this.data)
      this._renderRegionData("", dataset, t)
    },

    renderRegionData(region, regiondata, t) {
      const aggregated = this._mkLevelData(region, regiondata)

      const dataset = d3.values(aggregated)
      this._renderRegionData(region, dataset, t)

      this.current_region = aggregated[region]
    },

    _mkLevelData(parentid, data) {
      // re-aggregate the data to compute per-level stuff
      const out = {}
      const plen = parentid.length

      const _aggregate = (id, row) => {
        let item = out[id]
        if (item === undefined) {
          item = out[id] = {}

          for (const k in row) {
            // can't simply Object.assign, because of sets
            const v = row[k];

            if (v instanceof d3.set)
              item[k] = d3.set(v.values())
            else
              item[k] = v

            // overwrite id
            item.id = id
          }
        } else {
          for (const k in row) {
            const v = row[k]

            if (typeof v == 'string')
              continue
            else if (typeof v == 'number')
              item[k] += v
            else if (v instanceof d3.set)
              v.each(x => item[k].add(x))
              else
                console.error("Unhandled key / value", k, v)
          }
        }
      }

      for (const row of data) {
        const rlen = row.id.length
        let id

        if (rlen > plen) {
          // is this a descendant?
          if (row.id.substr(0, plen) != parentid) continue

          // if level1 aggregate under level0 (because yeah that makes sense)
          // else aggregate under the first(ish)-level descendants
          id = row.id.substr(0, rlen == 3 ? 2 :
                                            plen == 2 ? 4 : plen + 1)
        }

        else if (rlen < plen) {
          // is this an ancestor?
          if (parentid.substr(0, rlen) != parentid) continue

          // hardcoding again: level1s go under level0
          id = rlen === 3 ? row.id.substr(0, 2) : row.id
        }

        else { // if rlen == plen
          // am i me?
          if (row.id != parentid) continue

          id = row.id
        }

        _aggregate(id, row)
      }

      this.region_data = out

      return out
    },

    handleFilterBeneficiary(newid, oldid) {
      this.$super.handleFilterBeneficiary(newid, oldid);

      // hide the big circles, they're distractive
      const t = this.getTransition();
      this.chart.selectAll('g.states > g.beneficiary > g')
        .transition(t)
        .attr("opacity", Number(!newid));
    },

    handleFilterRegion(newid, oldid) {
      console.log(newid, oldid)
    },
  },
});
</script>
