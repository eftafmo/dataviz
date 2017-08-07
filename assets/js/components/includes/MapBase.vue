q<template>
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

      <g class="states" />
      <g class="regions" />

      <g class="top"> <!-- we need to draw the frames twice, for fill and stroke -->
        <g class="frames" />
      </g>

    </g>
  </svg>

  <slot></slot>

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

  // - strokes
  .with-boundary {
    stroke: #7f9fc8;
    // commented out this one because it's being set dynamically
    //stroke-width: 0.5;
    stroke-linejoin: round;
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



//@import './nightmap.less';



  .chart {
    .base {
      .sphere {
        fill: @water;
        stroke: none;
      }
      .graticule {
        stroke: #333;
        // commented out this because it's being set dynamically
        //stroke-width: .2;
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
      .with-boundary;

      .coastline {
        fill: none;
      }
      .countries {
        fill: @terrain;
      }
    }

    .states {
      .beneficiary {
        path {
          .with-boundary;
        }
      }

      .donor {
        stroke: @donor_stroke;
      }
    }

    .regions {
      // regions get their fill inline

      path {
        .with-boundary;
      }
    }
  }
}



body, header {background-color: #111 !important;}

</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

import ChartMixin from '../mixins/Chart';
import WithCountriesMixin from '../mixins/WithCountries';

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
    ChartMixin,
    WithCountriesMixin,
  ],

  props: {
    origin: {
      type: String,
      default: "",
    },

    render_states: {
      type: Boolean,
      default: true,
    },

    zoomable: {
      type: Boolean,
      default: true,
    },

    default_nuts_levels: {
      type: Array,
      default: () => [3],
    },

    donor_colour: {
      type: String,
      default: '#fff',
    },

    norway_colour: {
      type: String,
    },

    beneficiary_colour: {
      type: String,
      default: '#fff',

//default: null

    },

    region_colour: {
      type: String,
      default: "none",
    },
  },

  data() {
    return {
      base_rendered: false,
      states_rendered: false,
      regions_rendered: {},

      width: 800,
      height: 800,

      zoom_padding: .1,

      terrain_stroke: 0.5,
      graticule_stroke: 0.2,
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
      return this.base_rendered && (!this.render_states || this.states_rendered);
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
    // cache for computed geofeature-related data
    this.geodetails = {};
    // placeholders for fetched topojson data
    this.geo_data = {
      layers: null,
      regions: null,
    };
    // this will be updated real-time, don't make it observable
    this.current_zoom = 1;

    // aaand we can start fetching data already

    d3.json(this.origin + this.LAYERS_URL, (error, data) => {
      if (error) throw error;
      this.geo_data.layers = data;
      this.renderBase();
    });

    d3.json(this.origin + this.REGIONS_URL, (error, data) => {
      if (error) throw error;
      this.geo_data.regions = data;
      this.renderStates();
    });
  },

  mounted() {
    // create a stylesheet for dynamic changes
    this.stylesheet = document.createElement("style");
    this.$el.appendChild(this.stylesheet);

    //this.updateStyle(); // this is already triggered by the watched chartWidth

    this.$nextTick(this.render);
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

    render() {
      this.renderBase();
      this.renderStates();
    },

    renderBase() {
      // bail out if no data, or not mounted, or already rendered
      if (!this.geo_data.layers || !this.$el || this.base_rendered) return;

      const topo = _mk_topo_funcs(this.geo_data.layers);

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
      delete this.geo_data.layers;

      this.base_rendered = true;
    },

    renderStates() {
      // bail out if no data, or not mounted, or already rendered
      // also, well, if we shouldn't render.
      if (!this.render_states ||
          !this.geo_data.regions || !this.$el || this.states_rendered) return;

      const scale_LI = 5,
            frame_padding_LI = 1.7;

      const topo = _mk_topo_funcs(this.geo_data.regions);

      const path = this.path;

      const state_data = topo.features("nuts0").filter(
        // beneficiaries and donors
        d => this.COUNTRIES[d.id] !== undefined
      );

      const states = this.chart.select('.states').selectAll('g')
        .data(state_data)
        .enter()
        .append("g")
        .attr("class", d => `${this.COUNTRIES[d.id].type} ${d.id}` )
        .attr("opacity", 1)
        .on("mouseenter", this.$parent.stateEnter)
        .on("mouseleave", this.$parent.stateLeave)
        .on("click", this.$parent.stateClick)

        .append("path")
        .attr("d", path)
        .attr("fill", d => {
          if (this.isBeneficiary(d))
            return this.beneficiary_colour;

          if (d.id == "NO")
            return this.donor_colour_no;

          return this.donor_colour;
        })
        // while at this, cache the centroids and bounding box,
        // because the geo-data will get wiped during data manipulation
        .each(this.cacheGeoDetails);

      // magnify Liechtenstein
      const _li = this.geodetails["LI"];

      states.filter(d => d.id == "LI")
        .attr("vector-effect","non-scaling-stroke")
        .attr("transform", (d) => {
          const scale = scale_LI,
                // though incorrect, centroid looks better than center
                center = _li.centroid,
                tx = -center.x * (scale - 1),
                ty = -center.y * (scale - 1);
          return `translate(${tx},${ty}) scale(${scale})`;
        });

      // and give it a frame too. two actually.
      for (const layer of [".middle", ".top"]) {
        this.chart.select(layer).select(".frames")
          .append("circle")
          .attr("cx", _li.center.x)
          .attr("cy", _li.center.y)
          .attr("r",
                Math.max(_li.width, _li.height) / 2 *
                scale_LI * frame_padding_LI
               );
      }

      // we can delete the state data at this point, save a little memory
      //delete this.geo_data.regions.objects.nuts0;

      this.states_rendered = true;
    },

    renderRegions(state, levels) {
      // bail out if already rendered (or no data, or not mounted?)
      // TODO: do we want to remember rendering per nuts level?
      if (this.regions_rendered[state]) // || !this.geo_data.regions || !this.$el || ])
        return;

      if (levels === undefined) levels = this.default_nuts_levels;

      // using both enter and update selections, in case we decide
      // to render per nuts level
      const main = this.chart.select('.regions').selectAll('g.state.' + state)
              .data([state]),
            mentered = main
              .enter()
              .append('g')
              .attr("class", `state ${this.COUNTRIES[state].type} ${state}`)
              // start with these invisible
              .style("display", "none")
              .attr("opacity", 0);

      const layers = main.merge(mentered).selectAll("g.layer")
        .data(levels.map(x => ({ level: x }) ))
        .enter()
        .append("g")
        .attr("class", d => "layer level" + d.level)
        // start with these invisible too
        .style("display", "none")
        .attr("opacity", 0);

      const getRegionData = d => {
        // filter the topojson data for the current state.
        const level = d.level,
              data = this.geo_data.regions;
        // we're gonna create a new objects collection, so filtering
        // is done before computing the feature set
        const source = data.objects["nuts" + level],
              objects = {
                type: source.type,
                geometries: source.geometries.filter(
                  x => x.id.substr(0, 2) == state
                )
              };

        return topojson.feature(data, objects).features;
      }

      const regions = layers.selectAll("g")
        .data(getRegionData)
        .enter()
        .append("g")
        .attr("class", d => "region " + d.id)
        // don't forget to cache the stuff
        .each(this.cacheGeoDetails);

      regions
        .append("path")
        .attr("d", this.path)
        .attr("fill", this.region_colour);

      this.regions_rendered[state] = true;

      return regions;
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
      return this.width / this.chartWidth / this.current_zoom;
    },

    mkStyle() {
      const scaleFactor = this.getScaleFactor(),
            terrain_stroke = this.terrain_stroke * scaleFactor,
            graticule_stroke = this.graticule_stroke * scaleFactor;

      return `
        .viz.map .chart .terrain path,
        .viz.map .chart .states path,
        .viz.map .chart .regions path {
          stroke-width: ${terrain_stroke};
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
