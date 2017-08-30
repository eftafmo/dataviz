<template>
<chart-container :width="width" :height="height">
  <svg :viewBox="`0 0 ${width} ${height}`">
    <g class="chart">

      <g class="base">
        <path class="sphere" />
        <path class="graticule" />
        <g class="frames" />
      </g>

      <g class="terrain">
        <g class="countries" />
        <g class="territories" />
        <path class="coastline" /> <!-- make sure coastline is on top, just in case -->
      </g>

      <g class="middle"> <!-- some frames need drawing in different places -->
        <g class="frames" />
      </g>

      <g class="regions"></g>

      <g class="top"> <!-- we need to draw the frames twice, for fill and stroke -->
        <g class="frames" />
      </g>

    </g>

    <slot></slot>

  </svg>

  <slot name="after-map"></slot>

</chart-container>
</template>

<style lang="less">
// this is to be included only by the Map mixin, which uses this selector
.viz.map {
  // defs
  // - fills
  @water: #cbe9f6;
  @terrain: #fff;
  @donor_inactive: #85adcb;

  // - stroke widths. these are all overriden dynamically,
  //   but left here for reference
  @terrain_stroke_width: 0.7;
  @region_stroke_width: 0.4;
  @graticule_stroke_width: 0.2;

  // - strokes
  .with-boundary {
    stroke: #7f9fc8;
    stroke-linejoin: round;
  }

  .with-terrain-boundary {
    .with-boundary;
    //stroke-width: @terrain_stroke_width;
  }

  .with-region-boundary {
    .with-boundary;
    //stroke-width: @region_stroke_width;
  }

  @donor_stroke: #111;

  // - and others
  .frame-filled {
    fill: #d9f1f6;
  }
  .frame-stroked {
    stroke: #666;
    stroke-width: .5;
  }

  // styles
  .chart-container svg {
    box-shadow: 0px 0px 2px #aaa;
  }

  .chart {
    .base {
      .sphere {
        fill: @water;
        stroke: none;
      }
      .graticule {
        stroke: #333;
        //stroke-width: @graticule_stroke_width;
        stroke-opacity: .5;
        fill: none;
      }

      .frames {
        .frame-filled;
        stroke: none;
      }
    }

    .middle {
      .frames {
        //.frame-filled;
        fill: #dde;
        fill-opacity: .3;
      }
    }

    .top {
      .frames {
        fill: none;
       .frame-stroked;
      }
    }

    .terrain {
      .with-terrain-boundary;

      .coastline {
        fill: none;
      }
      .countries {
        fill: @terrain;
      }
    }

    .regions {
      .with-region-boundary;

      &.level0 {
        .with-terrain-boundary;
      }

      .donor {
        stroke: @donor_stroke;
      }
    }
  }
}

</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

import BaseMixin from '../mixins/Base'
import ChartMixin from '../mixins/Chart';
import {COUNTRIES, default as WithCountriesMixin} from '../mixins/WithCountries';

import ChartContainer from './ChartContainer';


// TODO: pass these through webpack maybe?
const LAYERS_URL = "/assets/data/layers.topojson";
const REGIONS_URL = "/assets/data/nuts2006.topojson";


function _mk_topo_funcs(data) {
  const layers = data.objects;

  return {
    mesh(layer, filter) {
      return topojson.mesh(data, layers[layer], filter);
    },

    features(layer) {
      return topojson.feature(data, layers[layer]).features;
    },
  };
}


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithCountriesMixin,
  ],

  props: {
    origin: {
      type: String,
      default: "",
    },

    // a combination of states / levels that should be rendered by default.
    // must be an array of {states, levels} objects.
    // a missing key will cause all_states / all_levels to get rendered
    initial_regions: {
      type: Array,
      default: () => [{}],
    },

    // all states used by this. set it to discard unused data.
    all_states: {
      type: Array,
      default: () => Object.keys(COUNTRIES).filter(x => x != "Intl"),
    },

    // all nuts levels used by this. set it to discard unused data.
    all_levels: {
      type: Array,
      default: () => [0, 1, 2, 3],
    },

    fillfunc: {
      type: Function,
      default: () => null
    },

    opacityfunc: {
      type: Function,
      default: () => null
    },

    zoomable: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      base_loaded: false,
      regions_loaded: false,

      base_rendered: false,
      regions_rendered: false,

      width: 800,
      height: 800,

      zoom_padding: .1,

      terrain_stroke_width: 0.8,
      region_stroke_width: 0.2,
      graticule_stroke_width: 0.2,

      LI_zoom_factor: 5,
    };
  },

  computed: {
    LAYERS_URL() {
      return this.origin + LAYERS_URL;
    },
    REGIONS_URL() {
      return this.origin + REGIONS_URL;
    },

    rendered() {
      return this.base_rendered && this.regions_rendered
    },

    can_render_base() {
      return this.base_loaded && this.is_mounted
    },

    can_render_regions() {
      return this.regions_loaded && this.is_mounted
    },

    donor_colour_no() {
      return this.norway_colour !== undefined ?
             this.norway_colour : this.donor_colour;
    },

    projection() {
      /*
       * "The European grid is a proposed, multipurpose Pan-European mapping standard.
       *  It is based on the ETRS89 Lambert Azimuthal Equal-Area projection coordinate
       *  reference system, with the centre of the projection at the point 52o N, 10o E
       *  and false easting: x0 = 4321000 m, false northing: y0 = 3210000 m
       *  (CRS identifier in Inspire: ETRS89-LAEA)."
       */
      // return d3.geoAzimuthalEqualArea()
      //          .rotate([-10, -52, 0])
      //          .scale(1000)

      // not precisely to spec, but fits everything
      return d3.geoAzimuthalEqualArea()
               .rotate([-9.9, -53.33, 0])
               .scale(1215)
               .translate([this.width/2.455, this.height/1.9975]);
    },

    path() {
      return d3.geoPath().projection(this.projection);
    },
  },

  created() {
    // initialise here things that we don't want obeserved:
    // - cache for computed geofeature-related data
    this.geodetails = {};
    // - placeholders for fetched topojson data
    this.geodata = {
      layers: null,
      regions: null,
    };
    // - remember what got rendered
    this._rendered_regions = []
    // - this will be updated real-time, don't make it observable
    this.current_zoom = 1;

    // trigger base & initial region rendering.
    // these will only run once, when the watched things go false -> true.
    const _base_unwatch = this.$watch("can_render_base", v => {
      this.renderBase()
      _base_unwatch()
    })

    const _regions_unwatch = this.$watch("can_render_regions", v => {
      for (const x of this.initial_regions) {
        this.renderRegions(x.states, x.levels)
      }
      _regions_unwatch()
    })

    // aaand we can start fetching data already
    d3.json(this.LAYERS_URL, (error, data) => {
      if (error) throw error;
      this.geodata.layers = data;
      this.base_loaded = true
    });

    d3.json(this.REGIONS_URL, (error, data) => {
      if (error) throw error;

      // discard unused level data
      Object.keys(data.objects).filter(
        x => this.all_levels.indexOf(Number(x.substr(-1))) === -1
      ).forEach(
        x => delete data.objects[x]
      )

      this.geodata.regions = data
      this.regions_loaded = true
    });
  },

  mounted() {
    // create a stylesheet for dynamic changes
    this.stylesheet = document.createElement("style");
    this.$el.appendChild(this.stylesheet);

    //this.updateStyle(); // this is already triggered by the watched chartWidth
  },

  methods: {
    cacheGeoDetails(d) {
      const path = this.path;

      const centroid = path.centroid(d),
            bounds = path.bounds(d);

      // bounds are an array of [x0, y0], [x1, y1]
      const x1 = bounds[0][0],
            x2 = bounds[1][0],

            y1 = bounds[0][1],
            y2 = bounds[1][1],

            dx = x2 - x1,
            dy = y2 - y1,

            cx = (x1 + x2) / 2,
            cy = (y1 + y2) / 2;

      this.geodetails[d.id] = {

        name: d.properties.name,

        width: dx,
        height: dy,

        center: {
          x: cx,
          y: cy,
        },

        centroid: {
          x: centroid[0],
          y: centroid[1],
        },
      };

      if (!this.zoomable) return;
      // since we're at this, let's calculate the zoom transform data too
      const w = this.width,
            h = this.height,

            spacing = Math.min(w, h) * this.zoom_padding,

            k = Math.min((w - spacing) / dx,
                         (h - spacing) / dy),

            x = w / 2 - cx * k,
            y = h / 2 - cy * k;

      this.geodetails[d.id].transform = {
        x: x,
        y: y,
        k: k,
      };
    },

    renderBase() {
      if (!this.can_render_base) {
        console.error("This should never happen, really")
        return
      }

      const topo = _mk_topo_funcs(this.geodata.layers);

      const base = this.chart.select('.base'),
            terrain = this.chart.select('.terrain'),
            top = this.chart.select('.top'),

            path = this.path;

      base.select(".sphere")
          .datum({ type: "Sphere" })
          .attr("d", path);

      base.select(".graticule")
          .datum(d3.geoGraticule())
          .attr("d", path);

      // handle the layers. they are:
      // - framemalta
      // - frameremote
      // - coasts
      // - countries
      // - cyprusnorth
      // - remoteterritories

      // the frames need to be drawn twice, because
      const _framedata = [
        topo.mesh("framemalta"),
        topo.mesh("frameremote"),
      ];
      for (const sel of [base, top]) {
        sel.select(".frames").selectAll("path")
           .data(_framedata)
           .enter()
           .append("path")
           .attr("d", path);
      }

      // coastlines get drawn as a mesh
      terrain.select(".coastline")
             .datum(topo.mesh("coasts"))
             .attr("d", path);

      // countries are filled
      // TODO: it's useless to use countries here, because the real remote
      // territories are fillless. so we'll need to use NUTS-0 anyway.
      // but we still need the terrain for non-EU countries, which is
      // provided here, yet the layers topojson doesn't have country names,
      // so we can't filter on those. meh. fix this?
      const countries = terrain.select(".countries").selectAll("path")
      for (const layer of ["countries",
                           "remoteterritories",
                           "cyprusnorth"]
      ) {
        countries
          .data(topo.features(layer))
          .enter()
          .append("path")
          .attr("d", path);
      }

      // we can delete the base layers at this point, save some memory
      delete this.geodata.layers;

      this.base_rendered = true
      this.$emit("base-rendered")
    },

    setupLI(sel) {
      // Liechtenstein needs a bit of magnification
      const scale = this.LI_zoom_factor,
            frame_padding = 1.7;

      const geo = this.geodetails[sel.datum().id];

      sel
        .attr("transform", (d) => {
          // though incorrect, centroid looks better than center
          const center = geo.centroid,
                tx = -center.x * (scale - 1),
                ty = -center.y * (scale - 1);
          return `translate(${tx},${ty}) scale(${scale})`
        })

      // and give it a frame too, or two
      if (this._li_setup) return

      d3.selectAll(".middle, .top").select(".frames")
        .append("circle")
        .attr("cx", geo.center.x)
        .attr("cy", geo.center.y)
        .attr("r",
              Math.max(geo.width, geo.height) / 2 *
              scale * frame_padding
        )

      this._li_setup = true
    },

    _cleanupGeoData(what) {
      const geodata = this.geodata.regions

      for (const lvl in what) {
        const idxs = what[lvl],
              obj = "nuts" + lvl,
              collection = geodata.objects[obj],
              geometries = collection.geometries;

        for (let i = idxs.length; i--; ) {
          geometries.splice(idxs[i], 1)
        }

        if (geometries.length) return
        // else this goes out
        delete geodata.objects[obj]
      }

      // can we clean everything then?
      for (const _ in geodata.objects) return
      // yes we can
      delete this.geodata.regions
    },

    renderRegions(states, levels) {
      if (!this.can_render_regions) {
        console.error("This should never happen either")
        return
      }

      if (typeof states === "string") states = [states]
      else if (!states || states.length === 0) states = this.all_states
      if (typeof levels === "number") levels = [levels]
      else if (!levels || levels.length === 0) levels = this.all_levels

      // skip everything already rendered
      // (the simpleton version: look only at the arguments)
      const _args = states.join("-") + "/" + levels.join("-")
      if(this._rendered_regions.indexOf(_args) !== -1)
        return
      else
        this._rendered_regions.push(_args)

      const $this = this

      // filter and classify the topojson data.
      // we're gonna flatten everything (place all layers at the same level),
      // and group data by its parent region

      function _getRoot(id) {
        return id.substr(0, 2)
      }

      function _getParent(id) {
        return id.length == 2 ? "" : id.substr(0, id.length - 1)
      }

      function _getChildrenLevel(id) {
        return id == "" ? 0 : id.length - 2 + 1
      }

      const collection = {}

      const _gcs = {} // garbage-collect this stuff
      for (const level of levels) {
        const source = this.geodata.regions.objects["nuts" + level]
        if (source === undefined) // this got fully garbage-collected
          continue
        const _gc = _gcs[level] = []

        // we could simply filter, but since we're iterating anyway,
        // let's clean up unneeded data
        source.geometries.forEach( (g, i) => { // we use the index for gc
          const state = g.id.substr(0, 2)
          if (states.indexOf(state) === -1) {
            // clean up stuff that's never gonna be needed
            if (states === this.all_states || this.all_states.indexOf(state) === -1)
              _gc.push(i)

            return
          }
          // always cleanup what gets rendered
          _gc.push(i)

          const parent = _getParent(g.id)
          let geoms = collection[parent]
          if (geoms === undefined) geoms = collection[parent] = []

          geoms.push(g)
        })
      }

      const containers = this.chart.select(".regions").selectAll("g")
        .data(Object.keys(collection), d => d)

      const centered = containers.enter()
        .append("g")
        .attr("class", d => {
          const cls = []
          if(d) {
            const r = _getRoot(d)
            cls.push(r)
            if (d != r) cls.push(d)
          }
          cls.push("level" + _getChildrenLevel(d))
          return cls.join(" ")
        })
        .attr("opacity", this.opacityfunc)

      const regions = containers.merge(centered).selectAll("path")
        .data(
          x => {
            const geodata = this.geodata.regions
            // this has to be a geometry collection
            const objects = {
              type: "GeometryCollection",
              geometries: collection[x],
            }
            return topojson.feature(geodata, objects).features
          },
          d => d.id
        )
        .enter()
        .append("path")
        .attr("class", d => `${this.COUNTRIES[d.id.substr(0, 2)].type} ${d.id}`)
        .attr("d", this.path)
        .attr("fill", this.fillfunc)
        // some hardcoding, because level-0 paths get opacity transitions
        .attr("opacity", d => d.id.length == 2 ? 1 : null)

        /*
        .on("mouseenter", () => this.$emit("enter", ...arguments))
        .on("mouseleave", () => this.$emit("leave", ...arguments))
        .on("click", () => this.$emit("click", ...arguments))
        */

        .each(function(d) {
          // don't forget to cache the stuff
          $this.cacheGeoDetails(d)

          const sel = d3.select(this)
          // handle liechtenstein if needed
          if (d.id.substr(0, 2) == "LI") $this.setupLI(sel)

          // and clear the geo-data, we don't need it
          sel.datum({
            id: d.id,
            name: d.properties.name,
          })
        })

      this._cleanupGeoData(_gcs)

      this.regions_rendered = true
      if (!regions.empty()) this.$emit("regions-rendered", regions)
    },

    zoomTo(id, eventfuncs, t) {
      if (eventfuncs instanceof d3.transition) {
        t = eventfuncs;
        eventfuncs = undefined;
      }

      let zoomFunc;
      if (eventfuncs) {
        zoomFunc = eventfuncs.zoom;
        delete eventfuncs.zoom;
      }

      const zoom = d3.zoom()
                     .on("zoom", () => {
                       this.chart.attr("transform", d3.event.transform);
                       this.current_zoom = d3.event.transform.k;
                       this.updateStyle();
                       if (zoomFunc) zoomFunc();
                     });
      for (const event in eventfuncs) {
        zoom.on(event, eventfuncs[event]);
      }

      let transformer = d3.zoomIdentity;

      if (id) {
        const d = this.geodetails[id].transform;
        transformer = transformer.translate(d.x, d.y)
                                 .scale(d.k);
      }

      const context = t ? this.chart.transition(t) : this.chart;

      zoom.transform(context, transformer);
    },

    updateStyle() {
      this.stylesheet.innerHTML = this.mkStyle();
    },

    getScaleFactor() {
      // don't make this computed, it changes too fast
      const k = this.chartWidth / this.width * this.current_zoom

      // for some reason strokes are really puny when zoomed in,
      // so let's fix this a bit.
      // { y = a x + b; x = 1 => y = 1; x = 20 => y = 2 }
      const modificator = this.current_zoom * 1 / 21 + 20 / 21

      return k / modificator
    },

    mkStyle() {
      const k = this.getScaleFactor(),
            terrain_stroke = this.terrain_stroke_width / k,
            region_stroke = this.region_stroke_width / k,
            graticule_stroke = this.graticule_stroke_width / k,

            LI_stroke = terrain_stroke / this.LI_zoom_factor;

      return `
        .viz.map .chart .terrain {
          stroke-width: ${terrain_stroke};
        }

        .viz.map .chart .regions {
          stroke-width: ${region_stroke};
        }

        .viz.map .chart .regions .level0 {
          stroke-width: ${terrain_stroke};
        }
        .viz.map .chart .regions .LI {
          stroke-width: ${LI_stroke};
        }

        .viz.map .chart .base .graticule {
          stroke-width: ${graticule_stroke};
        }
      `;
    },
  },

  watch: {
    chartWidth: "updateStyle",

    rendered: {
      immediate: true,
      handler(yes) {
        if(yes) this.$emit("rendered");
      }
    },
  },
});
</script>
