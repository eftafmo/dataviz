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

    </g>
  </svg>
</chart-container>
  <div v-if="hasData" class="dropdown">
    <dropdown filter="beneficiary" title="Select a country" :items="beneficiarydata"></dropdown>
  </div>
  <div class="legend">
    <ul class="legend-items">
      <li>
          <span v-if="!this.filters['fm']" class="square" :style="{background: fmcolour('eea-grants')}">
            <span class="triangle" :style="{borderTopColor: fmcolour('norway-grants')}"></span>
          </span>
          <!-- special handling because filters[fm] can't be used for in fmcolour -->
          <span  v-if="this.filters['fm']" >
            <span v-if="this.filters['fm']=='EEA Grants'" class="square" :style="{background: fmcolour('eea-grants')}"> </span>
            <span v-if="this.filters['fm']=='Norway Grants'" class="square" :style="{background: fmcolour('norway-grants')}"> </span>
          </span>
          Donor states
      </li>
      <li>
        <span class="square"></span>
        Beneficiary states
      </li>
    </ul>
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
        // commented out this because it's being set dynamically
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
      .beneficiary {
        cursor: pointer;

        &.zero {
          cursor: not-allowed;
        }

        path {
          .with-boundary;
        }

        &:hover path {
          .hovered;
        }
      }
    }

    .regions {
      cursor: pointer;
      // regions get their fill inline

      path {
        .with-boundary;

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
  .legend {
    ul{
      padding-left: 0;
    }

    li {
      list-style-type: none;
      display: inline-flex;
      align-items: center;
      margin-right: 2rem;
    }

    li:last-of-type{
      margin-right: 0;
    }

      .square {
        height: 20px;
        width: 20px;
        background: @beneficiary;;
        display: inline-block;
        margin-right: 1rem;
        position: relative;
      }
      .triangle {
        width: 0;
        height: 0;
        border-left: 14px solid transparent;
        border-right: 14px solid transparent;
        border-top: 14px solid;
        top: -2.1px;
        position: absolute;
        transform: rotate(135deg);
        left: -9.1px;
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
import WithCountriesMixin from './mixins/WithCountries';
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
    this.region_names = {};
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
      donor_colour_inactive: "#85adcb",
      region_colour_default: "#fff",
      beneficiary_colour_default: '#ddd',
      beneficiary_colour_hovered: '#9dccec',
      beneficiary_colour_zero: '#fff',
    };
  },

  computed: {
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

    // TODO: would be nice if the host was provided by some constant,
    // (or these guys were fully qualified)
    // (but note: we still need to consider the current protocol)

    let root = "";
    if (this.datasource) {
      const host = this.datasource.replace(/^(https?:)?\/\/([^\/]+)\/.*$/, '$2')
      console.log(this.datasource, host)
      root = location.protocol +'//' + host;
    }

    console.log(root)

    this.queue.defer( (callback) => {
      d3.json(root + LAYERS, (error, data) => {
        if (error) throw error;
        this.layers = data;
        this.renderBase();
      });
      callback(null);
    });
    this.queue.defer( (callback) => {
      d3.json(root + NUTS, (error, data) => {
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

      const countries = Object.keys(this.COUNTRIES);
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
      //this.updateStyle();

      // TODO: move these somewhere else, and don't hijack default render
      this.renderBase();
      this.renderStates();

      this.renderData();

      this.rendered = true;
    },

    updateStyle() {
      let style = this.dynamicStyle;
      if (!style) {
        style = document.createElement("style");
        this.$el.appendChild(style);
        this.dynamicStyle = style;
      }
      style.innerHTML = this.mkStyle();
    },

    getScaleFactor() {
      // don't make this computed, it changes too fast
      return this.width / this.svgWidth / this.realtimeZoom;
    },

    mkStyle() {
      const scaleFactor = this.getScaleFactor(),
            terrain_stroke = this.terrain_stroke * scaleFactor,
            graticule_stroke = this.graticule_stroke * scaleFactor;

      return `
        .map-viz .chart .terrain path,
        .map-viz .chart .states path,
        .map-viz .chart .regions path {
          stroke-width: ${terrain_stroke};
        }
        .map-viz .chart .base .graticule {
          stroke-width: ${graticule_stroke};
        }
      `;
    },

    tooltipTemplate() {
      throw new Error("Not implemented");
    },

    createTooltip() {
      let tip = d3.tip()
          .attr('class', 'd3-tip map')
          .html(this.tooltipTemplate)
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
            _features = (obj) => topojson.feature(data, obj).features,
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

      const states = this.chart.select('.states').selectAll('g')
             .data(
               _features(layers.nuts0).filter(
                 (d) => this.COUNTRIES[d.id] !== undefined
               ),
               (d) => d.id
             )
             .enter()
             .append("g")
             .attr("class", (d) => `${this.COUNTRIES[d.id].type} ${d.id}` )
             .attr("opacity", 1);

      const paths = states
             .append("path")
             .attr("fill", this.beneficiary_colour_default)
             .attr("d", path)
             // while at this, cache the centroids and bounding box,
             // because the geo-data will get wiped during data manipulation
             .each(this.cacheGeoDetails);

      paths
        .filter( (d) => d.id == "LI" )
        .call(magnifyLiechtenstein);

      // hardcoding the donor colours a bit, because we want to
      // transition them later
      paths
        .filter(this.isDonor)
        .attr("fill", (d) => (
          d.id == "NO" ? "url(#multi-fm)" : this.fmcolour("eea-grants") // §
        ) );

      /* mouse events */
      // (only beneficiaries get them)
      states
        .filter(this.isBeneficiary)
        .on("click", function (d) {
          $this.toggleBeneficiary(d, this);
        })
        .on('mouseenter', function(d, i) {
          d3.select(this).raise();
          $this.tip.show.call(this, d, i);
        })
        .on('mouseleave', this.tip.hide);
    },

    renderData(t) {
      // children should implement this as needed
      return;
    },

    renderRegions(t) {
      // renders NUTS-lvl3 regions for the selected country
      const $this = this;
      const state = this.filters.beneficiary;

      // only render the current state, but capture the rest for exit()
      const containers = this
        .chart.select('.regions').selectAll('g.state')
        .data(
          state ? [state] : [],
          (d) => d
        );

      const centered = containers
        .enter()
        .append('g')
        .attr('class', (d) => "state " + d )
        .attr('opacity', 0);

      const regions = centered
        .selectAll('g')
        .data(
          state ? this._region_borders[state] : [],
          (d) => d.id
        );

      regions.enter()
        .append('g')
        .each( (d) => {
          this.cacheGeoDetails(d);
          // remember the region name
          this.region_names[d.id] = d.properties.name;
        } )
        .on('mouseenter', function(d, i) {
          d3.select(this).raise();
          $this.tip.show.call(this, d, i);
        })
        .on('mouseleave', this.tip.hide)

        .append('path')
        .attr('d', this.path)
        .attr('fill', this.region_colour_default);

      containers.merge(centered)
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
        .attr('fill', this.region_colour_default)

      // finally,
      this.renderRegionData(t)
    },

    renderRegionData(t) {
      const state = this.filters.beneficiary;

      // this could be called by another filter.
      // bail out if no beneficiary selected.
      if (state === null) return;

      let dataset = this._region_data[state];

      // finally, trigger the whole logic
      if (dataset === undefined) {
        // reset the transition, data might arrive too late to use it.
        // TODO: run a throbber / suggest data loading somehow?
        t = undefined;

        // fetch the data, fill the cache, render
        const url = this.detailsDatasource.replace('XX', state);

        d3.json(url, (error, data) => {
          if (error) throw error;
          dataset = this._region_data[state] = data;
          this._renderRegionData(state, this.computeRegionData(dataset), t);
        } );
      } else {
        this._renderRegionData(state, this.computeRegionData(dataset), t);
      }
    },

    computeRegionData(regiondataset) {
      const _filters = d3.keys(this.filters).filter( (f) => f != 'beneficiary' );
      const dataset = this.filter(regiondataset, _filters);

      const aggregated = this.aggregate(
        dataset,
        ['id'],
        [
          'allocation',
          'project_count',
          {source: 'sector', destination: 'sectors', type: String, filter_by: 'is_not_ta'},
        ],
        true
      );

      return aggregated;
    },

    _renderRegionData(state, regiondata, t) {
      throw new Error("Not implemented");
    },

    handleFilterBeneficiary(val, old) {
      const $this = this,
            chart = this.chart,
            t = this.getTransition();

      let transformer = d3.zoomIdentity,
          k = 1, x, y;

      if (val) {
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
              h = $this.height;

        k = Math.min((w - spacing) / dx,
                     (h - spacing) / dy);

        x = w / 2 - _x * k;
        y = h / 2 - _y * k;

        transformer = transformer.translate(x, y).scale(k);
      }

      this.zoomLevel = k;

      const zoom = d3.zoom()
                     .on("zoom", () => {
                       chart.attr("transform", d3.event.transform);
                       this.realtimeZoom = d3.event.transform.k;
                       this.updateStyle();
                     })
                     .on("start", () => {
                       // fade out / in state layer and show regions
                       if (old)
                         this.chart.select('.states > g.beneficiary.' + old)
                             .transition(t)
                             .attr("opacity", 1);

                       if (val)
                         this.chart.select('.states > g.beneficiary.' + val)
                             .transition(t)
                             .attr("opacity", 0);

                       this.renderRegions(t)
                     })

      chart
        .transition(t)
        .call(zoom.transform, transformer);
    },

    handleFilterFm(val, old) {
      const t = this.getTransition();

      /*
       * part 0: re-render data-dependent stuff
       */
      this.renderData(t);

      /*
       * part 1: change the donor colours
       */

      // TODO: find a better way to deal with this. hardcoding is meh. §
      // (use ids everywhere)?
      const colourfuncEEA = () => val != "Norway Grants" ?
                                  this.fmcolour("eea-grants") :
                                  this.donor_colour_inactive;

      const colourfuncNO = val === null ?
                           (d) => this.fmcolour(d) :
                           () => this.fmcolour(slugify(val)); // awful §

      this.chart.select('.states').selectAll('path')
        .filter( (d) => this.isDonor(d.id) && d.id != "NO" )
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
      const t = this.getTransition();
      this.renderData(t);
      this.renderRegionData(t);
    },
  },

  watch: {
    svgWidth: "updateStyle",
  },
});
</script>
