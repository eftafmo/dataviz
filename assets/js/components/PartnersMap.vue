<template>
<div :class="[$options.type, { rendering: !rendered }]">
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

  <map-base
      ref="map"
      @rendered="handleMapRendered"
      @regions-rendered="registerEvents"
      :origin="origin"
      :all_levels="[3]"
      :fillfunc="fillfunc"
      :zoomable="false"
  >

    <template slot="after-map">
      <transition-group name="fade"
                        tag="div"
                        ref="container"
                        class="charts"
      >
        <div v-for="layer in layers"
             v-show="visible_layers.indexOf(layer) != -1"
             :key="layer"
             class="layer"
             :class="layer"
        ></div>
      </transition-group>

      <div ref="current" class="current"></div>
    </template>

  </map-base>

</div>
</template>


<style lang="less">
@duration: .5s;
@short_duration: .2s;

.viz.map.partners {
  .chart .regions {
    path {
      stroke-opacity: .5;
      pointer-events: all;
    }

    path.donor  {
      &:hover {
        stroke: #fff;
        stroke-opacity: 1;
      }
    }

    path.beneficiary {
      &:hover {
        stroke: #000;
        stroke-opacity: 1;
      }
    }

    path.partner {
      opacity: 0;
    }
  }

  .selector {
    margin-bottom: 1rem;
    display: flex;
    @media(max-width: 800px){
      display: block;
    }
     > label {
        display: inline-flex;
        @media(max-width:800px){
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
  input[type=checkbox]:checked + label:before { content: "✔"; } /* checked icon */
  #programmes {
    + label:before {
      color: rgb(8,153,0);
    }
  }

  #projects {
    + label:before {
      color: rgb(204,133,0);
    }
  }

  .charts, .current {
    &, * {
      position: absolute;
      left: 0;
      top: 0;

      width: 100%;
      height: 100%;

      pointer-events: none; // TODO: not enough on IE
    }

    canvas {
      display: block;
      opacity: 0;
      transition: opacity @short_duration;

      &.current {
        opacity: 1;
      }

      &.previous {
        opacity: 0;
      }
    }
  }


  .charts {
    transition: opacity @short_duration;
    opacity: 1;

    &.with-region {
      opacity: .3;
    }
  }
}
</style>


<script>
import * as d3 from 'd3';
import debounce from 'lodash.debounce';

import Chart from './Chart';

import PartnersMixin from './mixins/Partners';
import MapMixin from './mixins/Map';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';


export default Chart.extend({
  mixins: [
    PartnersMixin,
    MapMixin,
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
    };
  },

  computed: {
    chart_colours() {
      return this.getColours(this.chart_opacity, .5);
    },

    region_colours() {
      return this.getColours(this.region_opacity, .75);
    },

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
      // initially stored as dict to remove duplicates, now convert to array
      out.programmes = d3.values(out.programmes);
      out.projects = d3.values(out.projects);
      return out
    },
  },

  created() {
    // set up the canvas cache
    const ccache = {}
    for (const l of this.layers) {
      ccache[l] = {}
    }
    this._ccache = ccache

    this.renderCurrentRegion = debounce(this.renderCurrentRegion,
                                        this.renderWait.min)
  },

  methods: {
    fillfunc(d) {
      const id = d.id,
            country = id.substr(0, 2),
            type = this.COUNTRIES[country].type;

      return type == "donor" ? this.fmcolour("eea-grants") : "#fff"
    },

    getContainer(ref) {
      const c = this.$refs[ref];

      // if it's an element, it's a direct reference.
      // if it's a transition group, then it's a component.
      return c.$el ? c.$el : c;
    },

    getColours(opacity, pmod) {
      // projects modifier, because there's too many project lines
      // TODO: should alter the opacity based on line density instead
      if (!pmod) pmod = 1;

      const cs = {};
      for (const c in this.colours) {
        cs[c] = d3.color(this.colours[c]);
        cs[c].opacity = c != "projects" ? opacity : opacity * pmod;
      }

      return cs;
    },

    getRegionData(type, id) {
      const data = this.data[type];
      if (data === undefined) return;

      const out = [];
      for (const row of data) {
        if (row.source === id || row.target === id) {
          out.push(row);
        }
      }

      return out;
    },

    renderChart(redraw) {
      const $this = this,
            container = this.getContainer("container");

      // ideally we'd remove these onTransitionEnd, but ... ....
      d3.select(container).selectAll(".layer > canvas.previous")
        .remove()

      const prev = d3.select(container).selectAll(".layer > canvas:not(.previous)")
      if (redraw)
        prev.remove();
      else
        prev.attr("class", "previous");

      const charts = d3.select(container).selectAll(".layer")
        .data(this.layers) // we count on index order for match
        .append("canvas")
        .datum(d => d)
        .attr("width", this.chartWidth)
        .attr("height", this.chartHeight)
        .each(function(d) {
          const data = $this.data[d],
                colour = $this.chart_colours[d]
          $this.renderLayer(this, data, colour)
        })

      // fade in unless it's the initial render or a redraw
      // (and let css handle the transitions)
      if (!this.rendered || this.redraw)
        charts.attr("class", "current")
      else
        this.$nextTick(function(){ charts.attr("class", "current") })
    },

    renderCurrentRegion(r) {
      d3.select(this.getContainer("container"))
        .classed("with-region", r)

      const container = this.getContainer("current")

      d3.select(container).selectAll("canvas.previous")
        .remove()

      d3.select(container).selectAll("canvas:not(.previous)")
        .attr("class", "previous")

      if(!r) return;

      const canvases = []
      // don't bother rendering non-visible stuff
      for (const type of this.visible_layers) {
        // cache the canvas.
        // TODO: disabled for now. check memory usage.
        // it's seems surprisingly small in chrome, very high in firefox
        // (for ~450 canvases (data for ~400 regions))
        //let canvas = this._ccache[type][r];

        //if (canvas === undefined) {
          const data = this.getRegionData(type, r)

          // skip no-data
          if(!data || !data.length) continue

          //canvas = this._ccache[type][r] = document.createElement("canvas")
          const canvas = document.createElement("canvas")

          canvas.setAttribute("width", this.chartWidth)
          canvas.setAttribute("height", this.chartHeight)

          const colour = this.region_colours[type]

          this.renderLayer(canvas, data, colour)
        //}

        canvases.push(canvas)
      }

      for (const c of canvases) {
        if (c.parentNode) {
          // if it's already bound to the parent it was pending cleanup
          c.className = "current"
          continue
        }
        container.appendChild(c)
        this.$nextTick(function(){ c.className = "current" })
      }
    },

    renderLayer(canvas, data, colour) {
      if (data === undefined || data.length == 0) return;

      // note that setting the width or height causes the context
      // to be discarded. normally this is a fresh canvas and
      // the dimensions were set appropriately by vue, however
      // this might be a forced refresh during resizing
      if (canvas.width != this.chartWidth) {
        canvas.width = this.chartWidth
        canvas.height = this.chartHeight
      }

      const ctx = canvas.getContext("2d");

      const geodetails = this.map.geodetails
      const k = this.scale


      const _badids = d3.set();

      // no need to clear, it's done by setting the width & height
      //ctx.clearRect(0, 0, canvas.width, canvas.height);

      //ctx.fillStyle = colour;
      ctx.strokeStyle = colour;

      // for WebKit/Blink -based browsers
      try{
        ctx.setStrokeColor(colour);
      }
      catch(e) {
      }

      // make the line 1px wide, but scale down if necessary
      ctx.lineWidth = k > 1 ? 1 : Math.min(1, k * 2);

      ctx.beginPath();

      for (const d of data) {
        const i0 = d.source,
              i1 = d.target,
              o0 = geodetails[i0],
              o1 = geodetails[i1];

        if (o0 === undefined) _badids.add(i0);
        if (o1 === undefined) _badids.add(i1);
        if (o0 === undefined || o1 === undefined) continue;

        const p0 = o0.centroid,
              p1 = o1.centroid,

              x0 = p0.x * k,
              y0 = p0.y * k,

              x1 = p1.x * k,
              y1 = p1.y * k,

              // approximate the arc of a circle with radius equal to the distance
              // between p0 and p1, using a quadratic curve (a single control point)

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

        // a little hack for iceland - portugal links
        if (x < 0) {
          x = _mx + s * _ox / 2;
          y = _my - s * _oy / 2;
        }

        ctx.moveTo(x0, y0)
        ctx.quadraticCurveTo(x, y, x1, y1)

        //ctx.fillRect(x0 - 2, y0 - 2, 4, 4)
        //ctx.fillRect(x1 - 2, y1 - 2, 4, 4)
      }

      ctx.stroke();

      if (!_badids.empty())
        console.error("Unknown NUTS codes:", _badids.values());
    },

    registerEvents(selection) {
      const $this = this;

      const doMouse = (over) => {
        return function(d, i) {
          const sel = d3.select(this);

          if (over) {
            sel
              .raise()
            //$this.tip.show.call(this, d, i)
          } else {
            //$this.tip.hide.call(this, d, i)
          }

          $this.renderCurrentRegion(over ? d.id : null);
        }
      }

      selection.on("mouseenter", doMouse(true))
      selection.on("mouseleave", doMouse(false))
    },

    handleFilter() {
      this.render();
    },
  },

  watch: {
    chartWidth() {
      // re-render on resize. but don't hijack the initial render.
      if (!this.rendered) return

      this.renderChart(true)
      for (const l in this._ccache) {
        this._ccache[l] = {}
      }
    },
  },
});
</script>
