<template>
<div class="map-viz">
<chart-container :width="width" :height="height">
  <svg :viewBox="`0 0 ${width} ${height}`">
    <defs>
      <pattern id="multi-fm" width="50" height="50" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="50" height="25"
              class="Norway"
              :fill="colour('Norway')"
              :stroke="colour('Norway')"
        />
        <rect x="0" y="25" width="50" height="25"
              class="EEA"
              :fill="colour('EEA')"
              :stroke="colour('EEA')"
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

      <g class="regions" />

      <g class="top"> <!-- we need to draw the frames twice, for fill and stroke -->
        <g class="frames" />
      </g>

    </g>
  </svg>
</chart-container>
</div>
</template>

<style lang="less">
.map-viz {
  // defs
  // - fills
  @water: #cbe9f6;
  //@terrain: #f9f9cc;
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
  .chart {
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

    .regions {
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

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin, {get_flag_name, COUNTRIES} from './mixins/WithCountries';


// TODO: pass these through webpack maybe?
const LAYERS = "/assets/data/layers.topojson";
const NUTS = "/assets/data/nuts2006.topojson";


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithFMsMixin, WithCountriesMixin,
  ],

  beforeCreate() {
    // placeholders for fetched topojson data
    this.layers = null;
    this.borders = null;
  },

  props: {
  },

  data() {
    return {
      width: 800,
      height: 800,

      terrain_stroke: 0.5,
      graticule_stroke: 0.2,
      donor_inactive_colour: "#85adcb",

      zoom: 1,

       // there's no data needed for this visualisation
      dataset: {},
      hasData: true,
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
        this.borders = data;
        this.renderRegions();
      });
      callback(null);
    });
  },

  methods: {
    render() {
      // no reason to run this explicitly
      // because it's triggered by the change in svgWidth
      //this.setStyle();

      this.renderBase();
      this.renderRegions();

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
        .map-viz .chart .terrain, .map-viz .chart .regions {
          stroke-width: ${terrain_stroke};
        }
        .map-viz .chart .base .graticule {
          stroke-width: ${graticule_stroke};
        }`;
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
    },

    renderRegions() {
      // bail out if no data, or not mounted, or already rendered
      if (!this.borders || !this.$el || this._regions_rendered) return;
      this._regions_rendered = true;

      const $this = this,
            data = this.borders,
            layers = data.objects;

      const _mesh = (obj, filter) => topojson.mesh(data, obj, filter),
            _features = (obj) => topojson.feature(data, obj).features;

      const regions = this.chart.select('.regions'),
            path = this.path;

      const scaleLi = 5;

      function drawFrameLi(d) {
        const scale = scaleLi,
              center = path.centroid(d),
              cx = center[0],
              cy = center[1],
              bounds = path.bounds(d),
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
                  center = path.centroid(d),
                  cx = center[0],
                  cy = center[1],
                  tx = -cx * (scale - 1),
                  ty = -cy * (scale - 1);

            return `translate(${tx},${ty}) scale(${scale})`;
          })
          .each(drawFrameLi);
      }

      const countries = regions.selectAll("path")
             .data(_features(layers.nuts0).filter( (d) => COUNTRIES[d.id] ))
             .enter()
             .append("path")
             .attr("class", (d) => `${COUNTRIES[d.id].type} ${d.id}` )
             .attr("d", path);

      // remembering these for lazy reasons
      this._countrySelection = countries;

      countries
        .filter( (d) => d.id == "LI" )
        .call(magnifyLiechtenstein);

      countries
        .on("mouseenter",
            function(){ d3.select(this).raise(); }
        );

      countries
        .filter( (d) => COUNTRIES[d.id].type == "beneficiary" )
        .on("click", function (d) {
          $this.toggleBeneficiary(d.id, this);
        });

      // hardcoding the donor colours a bit, because we want to
      // transition them later
      countries
        .filter( (d) => COUNTRIES[d.id].type == "donor" )
        .attr("fill", (d) => d.id == "NO" ?
                             "url(#multi-fm)" : this.colour("EEA")
        );
    },

    handleFilterRegion(val, old) {
      const $this = this,
            chart = this.chart;

      const zoom = d3.zoom()
                     .on("zoom", () => {
                       chart.attr("transform", d3.event.transform);
                       this.zoom = d3.event.transform.k;
                       this.setStyle();
                     });

      chart
        .transition()
        .duration(500)
        .call(zoom.transform,
              transformer);

      function transformer() {
        const tr = d3.zoomIdentity;

        if (!val) return tr; // zooms out

        const spacing = .1 * Math.min($this.width, $this.height);

        const region = chart.select(".regions").select("." + val),
              bounds = $this.path.bounds(region.datum()),
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

      const colourfuncEEA = val != "Norway" ?
                            () => this.colour("EEA") :
                            () => this.donor_inactive_colour;

      const colourfuncNO = val === null ?
                           (d) => this.colour(d) :
                           () => this.colour(val);

      this._countrySelection
        .filter( (d) => COUNTRIES[d.id].type == "donor" && d.id != "NO" )
        .transition(t)
        .attr("fill", colourfuncEEA);

      // Norway uses a pattern fill
      d3.select(this.$el).select("svg > defs > pattern").selectAll("rect")
        .datum(function() { return this.getAttribute("class"); })
        .transition(t)
        .attr("fill", colourfuncNO)
        .attr("stroke", colourfuncNO);
    },
  },

  watch: {
    svgWidth: "setStyle",
  },
});
</script>
