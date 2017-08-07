<template>
<div :class="[$options.type, { rendering: !rendered }]">
  <h2>{{title}}</h2>

  <div class="selector">
    <p>Show:
      <label>
        <input type="checkbox" value="programmes" v-model="visible_layers">
        Donor programme partners
      </label>
      <label>
        <input type="checkbox" value="projects" v-model="visible_layers">
        Donor project partners
      </label>
    </p>
  </div>

  <map-base
      ref="map"
      v-on:rendered="mapRendered"
      :origin="origin"
      :render_states="true"
      :render_regions="true"
      :donor_colour="fmcolour('eea-grants')"
      :zoomable="false"
  >

    <transition name="fade" appear>
      <transition-group :key="changed"
                        name="fade"
                        tag="div"
                        ref="container"
                        class="charts"
                        :class="{'with-current': region}"
      >

        <canvas v-for="layer in layers"
                v-show="visible_layers.indexOf(layer) != -1"
                :key="layer"
                :class="layer"
                :width="chartWidth" :height="chartHeight"
        ></canvas>

      </transition-group>
    </transition>

    <transition name="fade-fast" appear>
      <div v-if="region"
           :key="region"
           ref="current"
           class="current"
      >
        <!-- render only the visible layer(s). supposedly people
             won't click the checkbox while hovering... -->
        <canvas v-for="layer in visible_layers"
                :class="layer"
                :width="chartWidth" :height="chartHeight"
        ></canvas>

      </div>
    </transition>

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
      pointer-events: visible;
    }

    g.region:hover path {
      stroke-opacity: 1;
    }

    .donor g.region {
      //path {
      //  stroke: #000;
      //}

      &:hover path {
        stroke: #fff;
      }
    }

    .beneficiary g.region {
      //path {
      //  stroke: #000;
      //}

      &:hover path {
        stroke: #000;
      }
    }
  }

  .charts, .current {
    &, canvas {
      position: absolute;
      left: 0;
      top: 0;

      width: 100%;
      height: 100%;

      pointer-events: none; // TODO: not enough on IE
    }

    canvas {
      display: block;

      // put the programmes on top, they're too faint
      &.programmes {
        z-index: 11;
      }
      &.projects {
        z-index: 10;
      }
    }
  }

  .charts {
    transition: opacity @short_duration;
    &.with-current {
      opacity: .3;
    }
    // ^^ that breaks .fade-* durations
    &.fade-enter-active, .fade-leave-active {
      transition: opacity @duration;
    }
  }

  .current {
.fade-fast-enter-active {
  transition: opacity 2s;
}


    .fade-fast-enter {
      opacity: .9,
    }
  }
}
</style>


<script>
import * as d3 from 'd3';

import Chart from './Chart';

import PartnersMixin from './mixins/Partners';
import MapMixin from './mixins/Map';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin from './mixins/WithCountries';

//
//import stuff from './partners-stuff.json';
//


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

      chart_opacity: .4,
      region_opacity: .8,

      title: 'Network map'
    };
  },

  computed: {
    chart_colours() {
      return this.getColours(this.chart_opacity);
    },

    region_colours() {
      return this.getColours(this.region_opacity);
    },

    scale() {
      return {
        x: this.chartWidth / this.width,
        y: this.chartHeight / this.height,
      };
    },

    data() {
//return stuff
      return {}
    },
  },

  methods: {
    getContainer(ref) {
      const c = this.$refs[ref];

      // if it's an element, it's a direct reference.
      // if it's a transition group, then it's a component.
      return c.$el ? c.$el : c;
    },

    getColours(opacity) {
      // massage the colours a bit
      const cs = {};
      for (const c in this.colours) {
        cs[c] = d3.color(this.colours[c]);
        cs[c].opacity = opacity;
      }

      // there's too many project lines
      // TODO: could alter the opacity based on density
      cs["projects"].opacity -= .1;

      return cs;
    },

    getRegionData(type, id) {
      const data = this.data[type];
      if (data === undefined) return;

      const out = [];
      for (const row of data) {
        if (row.source === id || row.target === id)
          out.push(row);
      }
      return out;
    },

    renderChart() {
      const $this = this,
            container = this.getContainer("container");

      // vue takes care of the canvas creation
      d3.select(container).selectAll("canvas")
        .each(function() {
          const type = this.className,
                data = $this.data[type],
                colour = $this.chart_colours[type];

          $this.renderLayer(this, data, colour)
        })
    },

    renderCurrentRegion(r) {
      const $this = this,
            container = this.getContainer("current");

      // vue takes care of the canvas creation
      d3.select(container).selectAll("canvas")
        .each(function() {
          const type = this.className,
                data = $this.getRegionData(type, r),
                colour = $this.region_colours[type];

          $this.renderLayer(this, data, colour)
        })
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
      ctx.lineWidth = 1;

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

              x0 = p0.x * k.x,
              y0 = p0.y * k.y,

              x1 = p1.x * k.x,
              y1 = p1.y * k.y,

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

          // let vue trigger the drawing
          $this.region = over ? d.id : null;
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
    map_rendered() {
      // TODO: this is convoluted, inefficient, belongs under MapBase,
      // and depends on render_states being true.
      // and needs to hang onto nuts0. (see MapBase.renderStates() at the end)
      // must ... fix ... :)
      for (const state of this.COUNTRY_ARRAY) {
        const regions = this.map.renderRegions(state.id);
        const layers = d3.selectAll(regions._parents);
        const container = d3.select(layers.node().parentNode)
        for (const sel of [regions, layers, container])
          sel.style("display", null)
             .attr("opacity", 1);

        regions.call(this.registerEvents)
      }
    },

    chartWidth() {
      // re-render on resize. but don't hijack the initial render.
      if (this.rendered) this.render();
    },

    region(r) {
      if (!r) return;
      // the canvases don't exist yet at this point
      this.$nextTick(() => this.renderCurrentRegion(r));
    },

    //
  },

});
</script>
