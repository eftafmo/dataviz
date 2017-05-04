<template>
<div class="map-viz">
  <svg :width="width" :height="height" class="chart">
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
    <g class="top"> <!-- we need to draw the frames twice, for fill and stroke -->
      <g class="frames" />
    </g>
  </svg>
</div>
</template>

<style lang="less">
.map-viz {
  .chart {
    .base {
      .sphere {
        fill: #cbe9f6; // beautiful planet
        stroke: none;
      }
      .graticule {
        stroke: #333; // with beautiful lines
        stroke-width: .2;
        stroke-opacity: .5;
        fill: none;
      }

      .frames {
        fill: #d9f1f6;
        stroke: none;
      }
    }

    .terrain {
      stroke: #7f9fc8;
      stroke-width: .5;

      .coastline {
        fill: none;
      }
      .countries {
        fill: #f9f9cc;
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

//
aside {display: none !important;}


</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithFMsMixin from './mixins/WithFMs';
import WithCountriesMixin, {get_flag_name} from './mixins/WithCountries';


// TODO: pass these through webpack maybe?
const LAYERS = "/assets/data/layers.topojson";
const NUTS = "/assets/data/nuts2006.topojson";


export default Vue.extend({
  beforeCreate() {
    // placeholders for fetched topojson data
    this.layers = null;
    this.borders = null;
  },

  mixins: [
    BaseMixin, ChartMixin,
    WithFMsMixin, WithCountriesMixin,
  ],

  props: {
  },

  data() {
    return {
      width: 800,
      height: 800,

       // there's no data needed for this visualisation
      dataset: {},
      hasData: true,
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
    this.queue.defer( (callback) => {
      d3.json(LAYERS, (error, data) => {
        if (error) throw error;
        this.layers = data;
        this.renderBase();
      });
      callback(null);
    });
  },

  methods: {
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

    main() {
      this.renderBase();
    },
  },
});
</script>
