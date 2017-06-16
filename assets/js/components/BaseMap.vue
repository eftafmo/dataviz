<template>
<div class="map-viz">
  <chart-container :width="width" :height="height" :class="{ rendering: !rendered }">
  <svg :viewBox="`0 0 ${width} ${height}`">
    <defs>
      <pattern id="multi-fm" width="50" height="50" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="50" height="25"
              class="norway-grants"
              :fill="fmcolour('norway-grants')"
              :stroke="fmcolour('norway-grants')"
        />
        <rect x="0" y="25" width="50" height="25"
              class="eea-grants"
              :fill="fmcolour('eea-grants')"
              :stroke="fmcolour('eea-grants')"
        />
      </pattern>
    </defs>

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

      <g class="states" />
      <g class="regions" />

      <g class="top"> <!-- we need to draw the frames twice, for fill and stroke -->
        <g class="frames" />
      </g>

      <g class="data" /> <!-- this one's for actual visualisations -->

    </g>
  </svg>
</chart-container>
  <div v-if="hasData" class="dropdown">
    <dropdown filter="beneficiary" title="Select a country" :items="COUNTRIES"></dropdown>
  </div>
</div>
</template>

<style lang="less">
.map-viz {
  // defs
  // - fills
  @water: #cbe9f6;
  @terrain: #fff;
  @beneficiary: #ddd;
  @hovered: #9dccec;
  @donor_inactive: #85adcb;
  // - strokes
  .with-boundary {
    stroke: #7f9fc8;
    // commented out this one because it's being set dynamically
    //stroke-width: 0.5;
    stroke-linejoin: round;
  }
  .hovered {
    stroke: #005494;
  }

  // styles
  .rendering {
    // don't show the base map until all data has been loaded
    // (TODO: we could also transition this)
    visibility: hidden;
  }

  .chart {
    .transitioning {
      pointer-events: none;
    }

    .base {
      .sphere {
        fill: @water;
        stroke: none;
      }
      .graticule {
        stroke: #333;
        // commented out this one because it's being set dynamically
        //stroke-width: .2;
        stroke-opacity: .5;
        fill: none;
      }

      .frames {
        fill: #d9f1f6;
        stroke: none;
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
      .with-boundary;
      cursor: pointer;

      /*
      // handled by d3
      .donor {
        fill: rgb(35, 97, 146),
      }
      .donor.NO {
        fill: url(#multi-fm);
      }
      */

      .beneficiary {
        fill: @beneficiary;
        &:hover {
          .hovered;
          fill: @hovered;
        }
      }
    }

    .regions {
      .with-boundary;
      cursor: pointer;
      // regions get their fill inline

      path {
        &:hover {
          stroke: black;
          //.hovered;
        }
      }
    }

    .top {
      .frames {
        fill: none;
        stroke: #666;
        stroke-width: .5;
      }
    }
  }
}
</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import {slugify} from 'js/lib/util'

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin, {get_flag_name, COUNTRIES} from './mixins/WithCountries';
import WithTooltipMixin from './mixins/WithTooltip';


// TODO: pass these through webpack maybe?
const LAYERS = "/assets/data/layers.topojson";
const NUTS = "/assets/data/nuts2006.topojson";


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithFMsMixin, WithCountriesMixin,
    WithTooltipMixin,
  ],

  beforeCreate() {
    // placeholders for fetched topojson data
    this.layers = null;
    this.regions = null;
    // cache for computed geofeature-related data
    this.geodetails = {};
    // cache for geojson data
    this._region_borders = {};
    // cache for allocation data
    this._region_data = {};
  },

  props: {
    // this is a "template" with the string 'XX' meant to be replaced
    // with the country code
    detailsDatasource: String,
  },

  data() {
    return {
      width: 800,
      height: 800,

      terrain_stroke: 0.5,
      graticule_stroke: 0.2,
      donor_inactive_colour: "#85adcb",
      default_region_colour: "#fff",

      zoom: 1,
    };
  },

  computed: {
    scaleFactor() {
      return this.width / this.svgWidth / this.zoom;
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
    // this needs to fetch some extra-data
    this.queue.defer( (callback) => {
      d3.json(LAYERS, (error, data) => {
        if (error) throw error;
        this.layers = data;
        this.renderBase();
      });
      callback(null);
    });
    this.queue.defer( (callback) => {
      d3.json(NUTS, (error, data) => {
        if (error) throw error;
        this.regions = data;
        this.renderStates();
        setTimeout(this._populateCache, 1);
      });
      callback(null);
    });
  },

  methods: {
    _populateCache() {
      // cache the nuts3-level geojson data, because extracting it
      // from topojson is an expensive operation
      const data = this.regions,
            layer = 'nuts3',
            cache = this._region_borders;

      const countries = Object.keys(COUNTRIES);
      countries.forEach( (c) => cache[c] = [] );

      const features = topojson.feature(data, data.objects[layer]).features;
      for (const f of features) {
        const c = f.id.substr(0,2);
        if (countries.indexOf(c) == -1) continue;
        cache[c].push(f);
      }
    },

    cacheGeoDetails(d) {
      const path = this.path;

      this.geodetails[d.id] = {
        centroid: path.centroid(d),
        bounds: path.bounds(d),
      };
    },

    render() {
      // no reason to run this explicitly
      // because it's triggered by the change in svgWidth
      //this.setStyle();

      // TODO: move these somewhere else, and don't hijack default render
      this.renderBase();
      this.renderStates();

      this.renderData();

      this.rendered = true;
    },

    setStyle() {
      let style = this.dynamicStyle;
      if (!style) {
        style = document.createElement("style");
        this.$el.appendChild(style);
        this.dynamicStyle = style;
      }

      const terrain_stroke = this.terrain_stroke * this.scaleFactor,
            graticule_stroke = this.graticule_stroke * this.scaleFactor;

      style.innerHTML = `
        .map-viz .chart .terrain,
        .map-viz .chart .states,
        .map-viz .chart .regions {
          stroke-width: ${terrain_stroke};
        }
        .map-viz .chart .base .graticule {
          stroke-width: ${graticule_stroke};
        }`;
    },

    createTooltip() {
      const $this = this;

      let tip = d3.tip()
          .attr('class', 'd3-tip map')
          .html(function(d) {
            // this function is common to both countries and regions, so...

            // not the smartest way to tell if this is a country, but it works
            // TODO: add country financial data
            // TODO: move flag to css
            if (d.id.length == 2)
              return `<div class="title-container">
                        <img src="/assets/imgs/${get_flag_name(d.id)}.png" />
                        <span class="name">${COUNTRIES[d.id].name}</span>
                      </div>
                      ${$this.format(d.total || 0)}`
                      +" <button class='btn btn-anchor'>X</button>";

            return `<div class="title-container">
                      <span class="name">${this.name} (${d.id})</span>
                    </div>
                    ${$this.format(d.amount || 0)}
                    <small>(Temporary)<small>`
                    +" <button class='btn btn-anchor'>X</button>";
          })
          .direction('n')
          .offset([0, 0])

       this.tip = tip;
       this.chart.call(this.tip)
    },

    renderBase() {
      // bail out if no data, or not mounted, or already rendered
      if (!this.layers || !this.$el || this._base_rendered) return;
      this._base_rendered = true;

      const data = this.layers,
            layers = data.objects;

      const _mesh = (obj, filter) => topojson.mesh(data, obj, filter),
            _features = (obj) => topojson.feature(data, obj).features;

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
      const _fd = [_mesh(layers.framemalta),
                   _mesh(layers.frameremote)];

      for (const sel of [base, top]) {
        sel.select(".frames").selectAll("path")
           .data(_fd)
           .enter()
           .append("path")
           .attr("d", path);
      };

      // coastlines get drawn as a mesh
      terrain.select(".coastline")
             .datum(_mesh(layers.coasts))
             .attr("d", path);

      // countries are filled
      // TODO: it's useless to use countries here, because the real remote
      // territories are fillless. so we'll need to use NUTS-0 anyway.
      // but we still need the terrain for non-EU countries, which is
      // provided here, yet the layers topojson doesn't have country names,
      // so we can't filter on those. meh. fix this?
      const countries = terrain.select(".countries").selectAll("path")
      for (const l of [layers.countries,
                       layers.remoteterritories,
                       layers.cyprusnorth]
      ) {
        countries
          .data(_features(l))
          .enter()
          .append("path")
          .attr("d", path);
      };

      this.renderStates();
    },

    renderStates() {
      // bail out if no data, or not mounted, or already rendered
      if (!this.regions || !this.$el || this._states_rendered) return;
      this._states_rendered = true;

      const $this = this,
            data = this.regions,
            layers = data.objects;

      const _mesh = (obj, filter) => topojson.mesh(data, obj, filter),
            _features = (obj) => topojson.feature(data, obj).features;

      const states = this.chart.select('.states'),
            path = this.path;

      const scaleLi = 5;

      function drawFrameLi(d) {
        const scale = scaleLi,
              center = $this.geodetails["LI"].centroid,
              cx = center[0],
              cy = center[1],
              bounds = $this.geodetails["LI"].bounds,
              b1 = bounds[0],
              b2 = bounds[1],
              dx = b2[0] - b1[0],
              dy = b2[1] - b1[1],
              r = Math.max(dx, dy) / 2 * scale * 1.5;

        $this.chart.select(".top").select(".frames")
             .append("circle")
             .attr("cx", cx)
             .attr("cy", cy)
             .attr("r", r);
      }

      function magnifyLiechtenstein(sel) {
        sel
          .attr("vector-effect","non-scaling-stroke")
          .attr("transform", (d) => {
            const scale = scaleLi,
                  center = $this.geodetails["LI"].centroid,
                  cx = center[0],
                  cy = center[1],
                  tx = -cx * (scale - 1),
                  ty = -cy * (scale - 1);

            return `translate(${tx},${ty}) scale(${scale})`;
          })
          .each(drawFrameLi);
      }

      const countries = states.selectAll("path")
             .data(
               _features(layers.nuts0).filter( (d) => COUNTRIES[d.id] ),
               (d) => d.id
             )
             .enter()
             .append("path")
             .attr("class", (d) => `${COUNTRIES[d.id].type} ${d.id}` )
             .attr("d", path)
             // while at this, cache the centroids and bounding box,
             // because the geo-data will get wiped during data manipulation
             .each(this.cacheGeoDetails);

      countries
        .filter( (d) => d.id == "LI" )
        .call(magnifyLiechtenstein);

      /* mouse events */
      countries
        .on("mouseenter",
            function(){ d3.select(this).raise(); }
        )
      countries
        .filter( (d) => COUNTRIES[d.id].type == "beneficiary" )
        .on("click", function (d) {
          $this.toggleBeneficiary(d.id, this);
        })
        // adding tooltip only for beneficiaries
        .on('mouseenter', this.tip.show)
        .on('mouseleave', this.tip.hide);

      // hardcoding the donor colours a bit, because we want to
      // transition them later
      countries
        .filter( (d) => COUNTRIES[d.id].type == "donor" )
        .attr("fill", (d) => d.id == "NO" ?
                             "url(#multi-fm)" : this.fmcolour("eea-grants") // §
        );
    },

    renderData() {
      // children should implement this as needed
      return;
    },

    renderRegions(t) {
      // renders NUTS-lvl3 regions for the selected country
      const $this = this;
      const state = this.filters.beneficiary;

      // only render the current state, but capture the rest for exit()
      const containers = this.chart.select('.regions').selectAll('g')
                             .data(
                               state ? [state] : [],
                               (d) => d
                             );

      const conentered = containers.enter()
                                   .append('g')
                                   .attr('class', (d) => d )
                                   .attr('opacity', 0);


      const regions = conentered.selectAll('path')
                                .data(
                                  state ? this._region_borders[state] : [],
                                  (d) => d.id
                                );

      const rentered = regions.enter().append('path')
             .attr('d', this.path)
             .each(this.cacheGeoDetails)
             // cache the name with the node
             .property('name', (d) => d.properties.name )
             .attr('fill', this.default_region_colour)
             .on('mouseenter',
                 function(d, i) {
                   d3.select(this).raise();
                   $this.tip.show.call(this, d, i);
                 }
             )
             .on('mouseleave', this.tip.hide);

      // don't add a title, it's shown by the tooltip
      //rentered
      // .append('title')
      // .text( (d) => d.properties.name );

      containers.merge(conentered)
                .style('display', null)
                .classed('transitioning', true)
                .transition(t)
                .attr('opacity', 1)
                .on('end', function() {
                  d3.select(this)
                    .classed('transitioning', false);
                });

      containers.exit()
                .classed('transitioning', true)
                .transition(t)
                .attr('opacity', 0)
                .on('end', function() {
                  d3.select(this)
                    .style('display', 'none')
                    .classed('transitioning', false);
                })

                // also reset regions to default colour
                .selectAll('path')
                .attr('fill', this.default_region_colour)

      // finally,
      this.renderRegionData(t)
    },

    renderRegionData(t) {
      // children should implement this as needed
      return;
    },

    handleFilterBeneficiary(val, old) {
      const $this = this,
            chart = this.chart,
            t = this.getTransition();

      const zoom = d3.zoom()
                     .on("zoom", () => {
                       chart.attr("transform", d3.event.transform);
                       this.zoom = d3.event.transform.k;
                       this.setStyle();
                     })
                     .on("start", () => this.renderRegions(t) )

      chart
        .transition(t)
        .call(zoom.transform,
              transformer);

      function transformer() {
        const tr = d3.zoomIdentity;

        if (!val) return tr; // zooms out

        const spacing = .1 * Math.min($this.width, $this.height);

        const bounds = $this.geodetails[val].bounds,
              x1 = bounds[0][0],
              x2 = bounds[1][0],

              y1 = bounds[0][1],
              y2 = bounds[1][1],

              dx = x2 - x1,
              dy = y2 - y1,

              _x = (x1 + x2) / 2,
              _y = (y1 + y2) / 2,

              w = $this.width,
              h = $this.height,

              k = Math.min((w - spacing) / dx,
                           (h - spacing) / dy),
              x = w / 2 - _x * k,
              y = h / 2 - _y * k;

        return tr.translate(x, y).scale(k);
      }
    },

    handleFilterFm(val, old) {
      const t = this.getTransition();

      /*
       * part 0: re-render data-dependent stuff
       */
      this.renderData();

      /*
       * part 1: change the donor colours
       */

      // TODO: find a better way to deal with this. hardcoding is meh. §
      // (use ids everywhere)?
      const colourfuncEEA = () => val != "Norway Grants" ?
                                  this.fmcolour("eea-grants") :
                                  this.donor_inactive_colour;

      const colourfuncNO = val === null ?
                           (d) => this.fmcolour(d) :
                           () => this.fmcolour(slugify(val)); // awful §

      this.chart.select('.states').selectAll('path')
        .filter( (d) => COUNTRIES[d.id].type == "donor" && d.id != "NO" )
        .transition(t)
        .attr("fill", colourfuncEEA);

      // Norway uses a pattern fill
      d3.select(this.$el).select("svg > defs > pattern").selectAll("rect")
        .datum(function() { return this.getAttribute("class"); })
        .transition(t)
        .attr("fill", colourfuncNO)
        .attr("stroke", colourfuncNO);

      /*
       * part 2: change the region data
       */

      this.renderRegionData(t);
    },

    handleFilter(type, val, old) {
      this.renderData();
      this.renderRegionData();
    },
  },

  watch: {
    svgWidth: "setStyle",
  },
});
</script>
