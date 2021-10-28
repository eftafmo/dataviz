<template>
  <chart-container :width="width" :height="height">
    <embeddor :period="period" tag="xmap" :svg-node="svgEl" />
    <svg
      :viewBox="`0 0 ${width} ${height}`"
      :class="`map-svg period-${period}`"
    >
      <g class="chart">
        <g class="base">
          <path class="sphere" />
          <path class="graticule" />
          <g class="frames" />
        </g>

        <g class="terrain">
          <g class="countries" />
          <g class="territories" />
          <path class="coastline" />
          <!-- make sure coastline is on top, just in case -->
        </g>

        <g class="middle">
          <!-- some frames need drawing in different places -->
          <g class="frames" />
        </g>

        <g class="regions"></g>

        <g class="top">
          <!-- we need to draw the frames twice, for fill and stroke -->
          <g class="frames" />
        </g>

        <slot></slot>
      </g>
    </svg>

    <slot name="after-map"></slot>
  </chart-container>
</template>

<script>
import * as d3 from "d3";
import * as topojson from "topojson-client";

import BaseMixin from "../mixins/Base";
import ChartMixin from "../mixins/Chart";
import {
  COUNTRIES,
  default as WithCountriesMixin,
} from "../mixins/WithCountries";

import ChartContainer from "./ChartContainer";
import Base from "../Base";
import Embeddor from "./Embeddor";

const URLS = {
  "2009-2014": {
    layersUrl: "data/layers2006.topojson",
    regionsUrl: "data/nuts2006.topojson",
  },
  "2014-2021": {
    layersUrl: "data/layers2016.topojson",
    regionsUrl: "data/nuts2016.topojson",
  },
};

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

export default {
  components: { Embeddor },
  extends: Base,
  mixins: [ChartMixin, WithCountriesMixin],
  props: {
    // a combination of states / levels that should be rendered by default.
    // must be an array of {states, levels} objects.
    // a missing key will cause all_states / all_levels to get rendered
    initialRegions: {
      type: Array,
      default: () => [{}],
    },

    // all states used by this. set it to discard unused data.
    allStates: {
      type: Array,
      default: () => Object.keys(COUNTRIES).filter((x) => x !== "Intl"),
    },

    // all nuts levels used by this. set it to discard unused data.
    allLevels: {
      type: Array,
      default: () => [0, 1, 2, 3],
    },

    fillfunc: {
      type: Function,
      default: () => null,
    },

    opacityfunc: {
      type: Function,
      default: () => null,
    },

    zoomable: {
      type: Boolean,
      default: true,
    },

    period: {
      type: String,
      required: true,
    },
  },
  emits: ["rendered", "base-rendered", "regions-rendered"],

  data() {
    return {
      svgEl: null,
      base_loaded: false,
      regions_loaded: false,

      base_rendered: false,
      regions_rendered: false,

      width: 800,
      height: 800,

      zoom_padding: 0.1,

      terrain_stroke_width: 0.8,
      region_stroke_width: 0.2,
      graticule_stroke_width: 0.2,

      LI_zoom_factor: 5,
    };
  },

  computed: {
    LAYERS_URL() {
      return this.getAssetUrl(URLS[this.period].layersUrl);
    },
    REGIONS_URL() {
      return this.getAssetUrl(URLS[this.period].regionsUrl);
    },

    rendered() {
      return this.base_rendered && this.regions_rendered;
    },

    can_render_base() {
      return this.base_loaded && this.is_mounted;
    },

    can_render_regions() {
      return this.regions_loaded && this.is_mounted;
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
      return d3
        .geoAzimuthalEqualArea()
        .rotate([-9.9, -53.33, 0])
        .scale(1215)
        .translate([this.width / 2.455, this.height / 1.9975]);
    },

    path() {
      return d3.geoPath().projection(this.projection);
    },
  },

  watch: {
    chartWidth: "updateStyle",

    rendered: {
      immediate: true,
      handler(yes) {
        if (yes) this.$emit("rendered");
      },
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
    this._rendered_regions = [];
    // - this will be updated real-time, don't make it observable
    this.current_zoom = 1;

    // trigger base & initial region rendering.
    // these will only run once, when the watched things go false -> true.
    const _base_unwatch = this.$watch("can_render_base", (v) => {
      this.renderBase();
      _base_unwatch();
    });

    const _regions_unwatch = this.$watch("can_render_regions", (v) => {
      for (const x of this.initialRegions) {
        this.renderRegions(x.states, x.levels);
      }
      _regions_unwatch();
    });

    // aaand we can start fetching data already
    fetch(this.LAYERS_URL).then((response) => {
      if (!response.ok)
        throw new Error(`${response.status} ${response.statusText}`);

      response.json().then((data) => {
        this.geodata.layers = data;
        this.base_loaded = true;
      });
    });

    fetch(this.REGIONS_URL).then((response) => {
      if (!response.ok)
        throw new Error(`${response.status} ${response.statusText}`);

      response.json().then((data) => {
        // discard unused level data
        Object.keys(data.objects)
          .filter((x) => this.allLevels.indexOf(Number(x.substr(-1))) === -1)
          .forEach((x) => delete data.objects[x]);

        this.geodata.regions = data;
        this.regions_loaded = true;
      });
    });
  },

  mounted() {
    // create a stylesheet for dynamic changes
    this.stylesheet = document.createElement("style");
    this.$el.appendChild(this.stylesheet);
    this.svgEl = this.$el.querySelector("svg.map-svg");

    //this.updateStyle(); // this is already triggered by the watched chartWidth
  },

  methods: {
    getZoomPadding(id) {
      // double the zoom padding for lower levels
      return this.zoom_padding * (id.length == 2 ? 1 : 2);
    },

    cacheGeoDetails(d) {
      const dId = d.id || d.properties.id;
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

      this.geodetails[dId] = {
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
        spacing = Math.min(w, h) * this.getZoomPadding(dId),
        k = Math.min((w - spacing) / dx, (h - spacing) / dy),
        x = w / 2 - cx * k,
        y = h / 2 - cy * k;

      this.geodetails[dId].transform = {
        x: x,
        y: y,
        k: k,
      };
    },

    renderBase() {
      if (!this.can_render_base) {
        console.error("This should never happen, really");
        return;
      }

      const topo = _mk_topo_funcs(this.geodata.layers);

      const base = this.chart.select(".base"),
        terrain = this.chart.select(".terrain"),
        top = this.chart.select(".top"),
        path = this.path;

      terrain.attr("stroke", "#87c3d5").attr("stroke-linejoin", "round");

      base
        .select(".sphere")
        .datum({ type: "Sphere" })
        .attr("d", path)
        .attr("fill", "#f6f6f6")
        .attr("stroke", "none");

      base
        .select(".graticule")
        .datum(d3.geoGraticule())
        .attr("d", path)
        .attr("stroke", "#333")
        .attr("stroke-opacity", 0.5)
        .attr("fill", "none");

      // handle the layers. they are:
      // - framemalta
      // - frameremote
      // - countries

      // the frames need to be drawn twice, because
      const _framedata = [topo.mesh("framemalta"), topo.mesh("frameremote")];
      for (const sel of [base, top]) {
        sel
          .select(".frames")
          .attr("fill", "none")
          .attr("stroke", "none")
          .selectAll("path")
          .data(_framedata)
          .enter()
          .append("path")
          .attr("d", path);
      }

      // countries are filled
      // TODO: it's useless to use countries here, because the real remote
      // territories are fill-less. so we'll need to use NUTS-0 anyway.
      // but we still need the terrain for non-EU countries, which is
      // provided here, yet the layers topojson doesn't have country names,
      // so we can't filter on those. meh. fix this?
      const countries = terrain.select(".countries").selectAll("path");
      countries
        .data(topo.features("countries"))
        .enter()
        .append("path")
        .attr("d", path)
        .attr("fill", "#dbf0f4");

      // we can delete the base layers at this point, save some memory
      delete this.geodata.layers;

      this.base_rendered = true;
      this.$emit("base-rendered");
    },

    setupLI(sel) {
      // Liechtenstein needs a bit of magnification
      const scale = this.LI_zoom_factor,
        frame_padding = 1.7;

      const gId = sel.datum().id || sel.datum().properties.id;
      const geo = this.geodetails[gId];

      sel.attr("transform", (d) => {
        // though incorrect, centroid looks better than center
        const center = geo.centroid,
          tx = -center.x * (scale - 1),
          ty = -center.y * (scale - 1);
        return `translate(${tx},${ty}) scale(${scale})`;
      });

      // and give it a frame too, or two
      if (this._li_setup) return;

      d3.selectAll(".middle, .top")
        .select(".frames")
        .append("circle")
        .attr("cx", geo.center.x)
        .attr("cy", geo.center.y)
        .attr(
          "r",
          (Math.max(geo.width, geo.height) / 2) * scale * frame_padding
        );

      d3.selectAll(".base .frames").attr("fill", "#d9f1f6");

      d3.selectAll(".middle .frames")
        .attr("fill", "#dde")
        .attr("fill-opacity", 0.3);

      d3.selectAll(".top .frames")
        .attr("fill", "none")
        .attr("stroke", "#666")
        .attr("stroke-width", 0.5);

      this._li_setup = true;
    },

    _cleanupGeoData(what) {
      const geodata = this.geodata.regions;

      for (const lvl in what) {
        const idxs = what[lvl],
          obj = "nuts" + lvl,
          collection = geodata.objects[obj],
          geometries = collection.geometries;

        for (let i = idxs.length; i--; ) {
          geometries.splice(idxs[i], 1);
        }

        if (geometries.length) return;
        // else this goes out
        delete geodata.objects[obj];
      }

      // can we clean everything then?
      for (const _ in geodata.objects) return;
      // yes we can
      delete this.geodata.regions;
    },

    renderRegions(regions, levels) {
      if (!this.can_render_regions) {
        console.error("This should never happen either");
        return;
      }

      if (typeof regions === "string") regions = [regions];
      else if (!regions || regions.length === 0) regions = this.allStates;
      if (typeof levels === "number") levels = [levels];
      else if (!levels || levels.length === 0) levels = this.allLevels;

      // skip everything already rendered
      // (the simpleton version: look only at the arguments)
      const _args = regions.join("-") + "/" + levels.join("-");
      if (this._rendered_regions.indexOf(_args) !== -1) return;
      else this._rendered_regions.push(_args);

      const $this = this;

      // filter and classify the topojson data.
      // we're gonna flatten everything (place all layers at the same level),
      // and group data by its parent region

      function _getParent(id) {
        return id.length === 2 ? "" : id.substr(0, id.length - 1);
      }

      function _getChildrenLevel(id) {
        return id === "" ? 0 : id.length - 2 + 1;
      }

      const collection = {};

      const _gcs = {}; // garbage-collect this stuff
      for (const level of levels) {
        const source = this.geodata.regions.objects["nuts" + level];
        if (source === undefined)
          // this got fully garbage-collected
          continue;
        const _gc = (_gcs[level] = []);

        // we could simply filter, but since we're iterating anyway,
        // let's clean up unneeded data
        source.geometries.forEach((g, i) => {
          const gId = g.id || g.properties.id;
          // we use the index for gc
          const state = gId.substr(0, 2);
          if (!this.allCountries[state]) return;

          if (regions.map((x) => x.substr(0, 2)).indexOf(state) === -1) {
            // clean up stuff that's never gonna be needed
            if (
              regions === this.allStates ||
              this.allStates.indexOf(state) === -1
            )
              _gc.push(i);

            return;
          }

          if (regions.find((r) => gId.substr(0, r.length) === r) === undefined)
            return;

          // always cleanup what gets rendered
          _gc.push(i);

          const parent = _getParent(gId);
          let geoms = collection[parent];
          if (geoms === undefined) geoms = collection[parent] = [];

          geoms.push(g);
        });
      }

      const containers = this.chart
        .select(".regions")
        .attr("stroke", "#87c3d5")
        .attr("stroke-linejoin", "round")
        .selectAll("g")
        .data(Object.keys(collection), (d) => d);

      const centered = containers
        .enter()
        .append("g")
        .attr("class", (d) => {
          const cls = [];
          // add the entire region tree as class names
          let r = d;
          while (r) {
            cls.push(r);
            r = _getParent(r);
          }
          cls.push("level" + _getChildrenLevel(d));
          return cls.join(" ");
        })
        .attr("opacity", this.opacityfunc);

      const shapes = containers
        .merge(centered)
        .selectAll("path")
        .data(
          (x) => {
            const geodata = this.geodata.regions;
            // this has to be a geometry collection
            const objects = {
              type: "GeometryCollection",
              geometries: collection[x],
            };
            return topojson.feature(geodata, objects).features;
          },
          (d) => d.id || d.properties.id
        )
        .enter()
        .append("path")
        .attr("class", (d) => {
          const dId = d.id || d.properties.id;
          return `${this.COUNTRIES[dId.substr(0, 2)].type} ${dId}`;
        })
        .attr("d", this.path)
        .attr("fill", this.fillfunc)
        .attr("opacity", 1)
        .attr("stroke", (d) => {
          const dId = d.id || d.properties.id;
          return this.COUNTRIES[dId.substr(0, 2)].type === "donor"
            ? "#111"
            : "inherit";
        })

        /*
        .on("mouseenter", () => this.$emit("enter", ...arguments))
        .on("mouseleave", () => this.$emit("leave", ...arguments))
        .on("click", () => this.$emit("click", ...arguments))
        */

        .each(function (d) {
          // don't forget to cache the stuff
          $this.cacheGeoDetails(d);

          const sel = d3.select(this);
          const dId = d.id || d.properties.id;

          // handle liechtenstein if needed
          if (dId.substr(0, 2) === "LI") $this.setupLI(sel);

          // and clear the geo-data, we don't need it
          sel.datum({
            id: dId,
            name: d.properties.name,
          });
        });

      this._cleanupGeoData(_gcs);

      this.regions_rendered = true;
      this.updateStyle();
      if (!shapes.empty()) this.$emit("regions-rendered", shapes);
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

      const zoom = d3.zoom().on("zoom", (ev) => {
        this.chart.attr("transform", ev.transform);
        this.current_zoom = ev.transform.k;
        if (zoomFunc) zoomFunc();
        this.updateStyle();
      });
      for (const event in eventfuncs) {
        zoom.on(event, eventfuncs[event]);
      }

      let transformer = d3.zoomIdentity;

      if (id) {
        const d = this.geodetails[id].transform;
        transformer = transformer.translate(d.x, d.y).scale(d.k);
      }

      const context = t ? this.chart.transition(t) : this.chart;

      zoom.transform(context, transformer);
    },

    updateStyle() {
      const k = this.getScaleFactor();
      const terrain_stroke = this.terrain_stroke_width / k;
      const region_stroke = this.region_stroke_width / k;
      const graticule_stroke = this.graticule_stroke_width / k;
      const LI_stroke = terrain_stroke / this.LI_zoom_factor;

      d3.selectAll(".dataviz .viz.map .chart .terrain").attr(
        "stroke-width",
        terrain_stroke
      );
      d3.selectAll(".dataviz .viz.map .chart .regions").attr(
        "stroke-width",
        region_stroke
      );
      d3.selectAll(".dataviz .viz.map .chart .regions .level0").attr(
        "stroke-width",
        terrain_stroke
      );
      d3.selectAll(".dataviz .viz.map .chart .regions .LI").attr(
        "stroke-width",
        LI_stroke
      );
      d3.selectAll(".dataviz .viz.map .chart .base .graticule").attr(
        "stroke-width",
        graticule_stroke
      );
    },

    getScaleFactor() {
      // don't make this computed, it changes too fast
      const k = (this.chartWidth / this.width) * this.current_zoom;

      // for some reason strokes are really puny when zoomed in,
      // so let's fix this a bit.
      // { y = a x + b; x = 1 => y = 1; x = 20 => y = 2 }
      const modificator = (this.current_zoom * 1) / 21 + 20 / 21;

      return k / modificator;
    },
  },
};
</script>

<style lang="less">
// this is to be included only by the Map mixin, which uses this selector
.dataviz .viz.map {
  // styles
  .chart-container {
    // don't let the map overflow the available height
    // (this works only if the map is square)
    max-width: 100vh;

    svg {
      box-shadow: 0 0 2px #aaa;
    }
  }
}

.map-svg.period-2014-2021 .HU {
  cursor: not-allowed !important;
}
</style>

