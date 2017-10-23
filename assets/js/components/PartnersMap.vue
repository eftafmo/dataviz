<template>
<div :class="classNames">
  <slot name="title" v-if="!this.embedded"></slot>

  <div class="selector">
    Show:
      <label>
        <input type="checkbox" value="programmes" id="programmes" v-model="visible_layers">
        <label for="programmes"></label>
        Donor programme partners
      </label>
      <label>
        <input type="checkbox" value="projects" id="projects" v-model="visible_layers">
        <label for="projects"></label>
        Donor project partners
      </label>
  </div>

  <pijama-defs ref="defs"></pijama-defs>

  <map-base
      ref="map"
      @rendered="handleMapRendered"
      @regions-rendered="registerEvents"
      :origin="origin"
      :all_levels="[3]"
      :fillfunc="fillfunc"
      :zoomable="false"
  >

    <g class="partnerships">
      <g v-for="layer in layers"
         :class="layer"
         class="base"
      ></g>
    </g>

  </map-base>

</div>
</template>


<style lang="less">
@duration: .5s;
@short_duration: .2s;

.dataviz .viz.map.is-partners {
  .chart .regions {
    path {
      stroke-opacity: .5;
      pointer-events: all;
    }

    path.donor {
      &:not(.zero):hover {
        stroke: #fff;
        stroke-opacity: 1;
      }
    }

    path.beneficiary, path.partner {
      &.zero {
        fill: none;
        stroke: none;
      }

      &:not(.zero):hover {
        stroke: #000;
        stroke-opacity: 1;
      }
    }
  }

  .partnerships {
    stroke-width: 1.5; // TODO: make it dynamic
    fill: none;
    pointer-events: none;
  }

  .selector {
    margin-bottom: 1rem;
    -js-display: flex;
    display: flex;
    @media(max-width: 800px){
      display: block;
    }
     > label {
        display: inline-flex;
        @media(max-width:800px){
          -js-display: flex;
          display: flex;
        }
        margin-left: 1rem;
      }
  }

  input[type=checkbox] { display:none; } /* to hide the checkbox itself */
  input[type=checkbox] + label:before {
    display: inline-block;
  }

  input[type=checkbox] + label {
    display: inline-block;
    border: solid #ddd;
    height: 19px;
    width: 19px;
    margin-right: .4rem;
    margin-top: -2px;
    position: relative;
  }

  input[type=checkbox] + label:before {
   content: "" "";
   font-size: 2.5rem;
   position: absolute;
   top: 50%;
   left: 50%;
   transform: translate(-50%,-50%);
  }
  input[type=checkbox]:checked + label:before { content: "✔\fe0e"; } /* checked icon */
  #programmes {
    + label:before {
      color: #089900;
    }
  }

  #projects {
    + label:before {
      color: #e68a00;
    }
  }
}
</style>


<script>
import * as d3 from 'd3';
import debounce from 'lodash.debounce';
import {slugify} from 'js/lib/util'

import BaseMap from './BaseMap'

import PartnersMixin from './mixins/Partners';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';


export default BaseMap.extend({
  mixins: [
    PartnersMixin,
    WithFMsMixin, WithCountriesMixin,
  ],

  props: {
    layers: {
      type: Array,
      default: () => ["programmes", "projects"],
    },
  },

  data() {
    return {
      visible_layers: this.layers,
      region: null,

      chart_opacity: 1.0,
      region_opacity: .8,

      default_opacity: .8,
    };
  },

  computed: {
    scale() {
      return this.chartWidth / this.width;
    },

    data() {
      const out = {
        programmes: {},
        projects: {},
      }

      const dataset = this.filtered;
      for (const d of dataset) {
        for (const po_code in d.PO) {
          if (d.DPP_nuts) {
            // we can have rows with PO but not DPP (only projects)
            out.programmes[d.DPP_nuts+d.PO[po_code].nuts] = {
              'source': d.DPP_nuts,
              'target': d.PO[po_code].nuts,
            };
          }
        }
        for (const prj_nuts of d.prj_nuts) {
          if (prj_nuts.dst) {
            // many project partners don't have nuts. let them be
            // we do want to see donor project partners with no nuts, though
            out.projects[prj_nuts.src+prj_nuts.dst] = {
              'source': prj_nuts.src,
              'target': prj_nuts.dst,
            }
          }
        }
      }

      // re-aggregate the data in both directions.
      // we'll use this for d3's data binding.
      const sources = {},
            targets = {}

      for (const type in out) {
        const data = d3.values(out[type])

        sources[type] = this.aggregate(
          data,
          [{source: 'source', destination: 'id'}],
          [{source: 'target', destination: 'regions', type: String}]
        )
        targets[type] = this.aggregate(
          data,
          [{source: 'target', destination: 'id'}],
          [{source: 'source', destination: 'regions', type: String}]
        )
      }

      return {sources, targets}
    },
  },

  mounted() {
    // make remote territories visible
    // this is very ugly. TODO: fix... somehow.. better
    this.chart.attr('transform', 'translate(60,0)')
  },

  methods: {
    tooltipTemplate(d) {
      const country = this.getAncestorRegion(d.id, 0)

      return `
        <div class="title-container">
          <svg>
            <use xlink:href="#${ this.get_flag_name(country) }" />
          </svg>
          <span class="name">${ this.getRegionName(d.id) } (${ d.id })</span>
        </div>`
    },

    renderChart() {
      const t = this.getTransition()

      this.renderDonorColours(t)
      this.renderRegionData(t)
      this.renderConnections(t)
      this.renderVisibleLayers(t)
    },

    renderRegionData(t) {
      // "render". this only updates the data
      // so the toolip works
      const dataset = this.data

      // merge the datasets to feed d3
      const data = {}

      for (const collection in dataset) {
        for (const type in dataset[collection]) {
          for (const id in dataset[collection][type]) {
            const row = dataset[collection][type][id]

            let item = data[id]
            if (item === undefined)
              item = data[id] = {
                id: id,
                states: {},
              }

            const states = d3.set()
            row.regions.each(x => states.add(this.getAncestorRegion(x, 0)))
            item.states[type] = states
          }
        }
      }

      const regions = this.chart.selectAll('.regions > g > path')
                          .data(d3.values(data), d => d.id)

      regions
        .classed("zero", false)

      regions
        .exit()
        .classed("zero", true)
        .each(function(d) {
          // reset data
          delete d.states
        })
    },

    renderConnections(t) {
      // we render from the donor side
      const conndata = this.data.sources

      for (const type in conndata) {
        this._renderConnections(type, d3.values(conndata[type]), t)
      }
    },

    _renderConnections(type, data, t) {
      const container = this.chart.select(`.partnerships > .${ type }`),
            regions = container.selectAll('g')
                               .data(data, d => d.id)

      const getColour = d => {
        const colour = this.colours[type]

        if (!this.filters.fm)
          return colour

        const country = this.getAncestorRegion(d.id, 0),
              fms = this.COUNTRIES[country].fms

        if (!fms || fms.indexOf(slugify(this.filters.fm)) === -1) {
          return this.weak_colours[type]
        }
        else
          return colour
      }

      // group connections by source region. will help us transition
      // to grayscale when filtering by fm
      const rentered = regions.enter()
                              .append('g')
                              .attr('class', d => {
                                const country = this.getAncestorRegion(d.id, 0),
                                      fms = this.COUNTRIES[country].fms
                                let out = d.id
                                if (fms) out += " " + fms.join(" ")
                                return out
                              })
                              .attr('stroke', getColour)

      regions
        .transition(t)
        .attr('stroke', getColour)

      const rexit = regions.exit().remove()

      const connections = regions.merge(rentered).selectAll('path')
                                 .data(
                                   // make the path aware of the source
                                   d => d.regions.values().map(
                                     x => ({src: d.id, dst: x})
                                   ),
                                   d => d.src + '-' + d.dst
                                 )

      const _badids = d3.set()

      const getArc = (src, dst) => { // TODO: memoize this
        // the simple approach would be to draw an arc with the same radius
        // as the distance between points, but we're gonna use a quadratic
        // curve instead, which allows us to mess with the arc's radius
        // programatically §
        // (also, we can use the same calculations to draw into a canvas)

        const geodetails = this.map.geodetails

        const o0 = geodetails[src],
              o1 = geodetails[dst]

        if (o0 === undefined) _badids.add(i0);
        if (o1 === undefined) _badids.add(i1);
        if (o0 === undefined || o1 === undefined) return

        const k = 1 // this.scale if drawing into a canvas

        const p0 = o0.centroid,
              p1 = o1.centroid,

              x0 = p0.x * k,
              y0 = p0.y * k,

              x1 = p1.x * k,
              y1 = p1.y * k,

              // distance between points
              _dx = x1 - x0,
              _dy = y1 - y0,

              // radius
              r = Math.sqrt(_dx * _dx + _dy * _dy),

              // sign
              s = (x1 >= x0) ? 1 : -1,

              // midpoint
              _mx = (x0 + x1) / 2,
              _my = (y0 + y1) / 2,

              // distance from midpoint (perpendicular)
              _d = r * (1 - Math.sqrt(3) / 2) * 2,

              // actual offsets from midpont
              _ox = _dy * (_d / (r)),
              _oy = _dx * (_d / (r));

        // the control point
        let x = _mx + s * _ox,
            y = _my - s * _oy;

        // a little hack for iceland - portugal links §
        if (x < 0) {
          x = _mx + s * _ox / 2;
          y = _my - s * _oy / 2;
        }


        //return `M ${ x0 },${ y0 } A ${ r },${ r } 0 0,${ (s + 1) / 2 } ${ x1 },${ y1 }`
        return `M ${ x0 },${ y0 } Q ${ x },${ y } ${ x1 },${ y1 }`

        ctx.quadraticCurveTo(x, y, x1, y1)
      }

      // because performing transitions on hundreds of paths kills rendering,
      // connections that enter / exit will instead be moved to a different
      // layer, and transitioned all at once

      const connentered = connections.enter()
        .append('path')
        .attr('class', d => d.dst)
        .attr('d', d => getArc(d.src, d.dst))

      // (some error checking)
      if (!_badids.empty())
        console.error("Unknown NUTS codes:", _badids.values());

      const connexit = connections.exit().remove()

      // buuut don't go through the craziness if there's nothing to transition
      if (t.duration() == 0) return

      const transitionConnections = (selection, newstuff) => {
        if (selection.empty()) return

        // shallow clone the container
        const baselayer = container.node(),
              newlayer = baselayer.cloneNode(false)

        // insert the clone before the original if pending removal,
        // or after if the stuff is new
        baselayer.parentNode.insertBefore(newlayer,
                                          newstuff ? baselayer.nextSibling : baselayer)

        // if exiting, this is a good time to add the fully-removed regions
        if (!newstuff) {
          rexit.each(function() {
            newlayer.appendChild(this)
          })
        }

        if (newstuff) newlayer.setAttribute('opacity', 0)

        // we're gonna move all the exit nodes under the new layer, but
        // we must clone each parent group as well, so...
        // instead of looping over connexit.nodes() and chasing each parent,
        // we'll using d3's beautifulous internals, which are structured
        // exactly the way we want them

        selection._groups.forEach(function(group, i) {
          // filter out empty elements
          group = group.filter(x => true)
          if (!group.length) return

          const parent = selection._parents[i],
                newparent = parent.cloneNode(false)
          newlayer.appendChild(newparent)

          for (const connection of group) {
            newparent.appendChild(connection)
          }
        })

        const exitfunc = function() {
          this.remove()
        }

        const enterfunc = function() {
          const parents = this.querySelectorAll('g')

          for (const parent of parents) {
            const selector = parent.getAttribute("class")
                                   .split(" ").map(c => "." + c).join("")

            const baseparent = baselayer.querySelector('g' + selector)
            // also bring the parent to front, avoids some flicker
            baseparent.parentNode.appendChild(baseparent)

            while (parent.firstChild) {
              baseparent.appendChild(parent.firstChild)
            }
          }

          this.remove()
        }

        // we need to delay things a bit or d3 gets very confused
        this.$nextTick( () =>
          d3.select(newlayer)
            .classed("base", false)
            .classed(newstuff ? "new" : "old", true)
            .transition(t)
            .attr('opacity', newstuff ? this.default_opacity : 0)
            .on('end', newstuff ? enterfunc : exitfunc)
        )
      }

      // FIXME: there's something broken with the enter, leaving as is for now
      //transitionConnections(connentered, true)
      transitionConnections(connexit, false)

    },

    registerEvents(selection) {
      const $this = this;

      const doMouse = (over) => {
        return function(d, i) {
          const self = d3.select(this)

          // disable when zeroed
          if (self.classed("zero")) return

          if (over) {
            self.raise()
            $this.tip.show.call(this, d, i)
          } else {
            $this.tip.hide.call(this, d, i)
          }

          //$this.renderCurrentRegion(over ? d.id : null);
        }
      }

      selection.on("mouseenter", doMouse(true))
      selection.on("mouseleave", doMouse(false))
    },

    renderVisibleLayers(t) {
      if (t === undefined) t = this.getTransition()

      for (const layer of this.layers) {
        this.chart.select(`.partnerships > .${ layer }`)
          .transition(t)
          .attr('opacity', this.visible_layers.indexOf(layer) === -1 ?
                0 : this.default_opacity)
      }
    },

    handleLayers() {
      this.renderVisibleLayers()
    },

    handleFilter() {
      this.render();
    },
  },

  watch: {
    visible_layers: "handleLayers",

    chartWidth() {
      // re-render on resize. but don't hijack the initial render.
      if (!this.rendered) return

      this.renderChart()
    },
  },
});
</script>
