<script>
import * as d3 from 'd3';
import {interpolateYlGn} from 'd3-scale-chromatic';

import BaseMap from './BaseMap';


export default BaseMap.extend({
  type: "grants",

  data() {
    return {
      nuts_level: 3,
      draw_nuts_levels: [3],

      beneficiary_colour_default: "#ddd",
      beneficiary_colour_hovered: "#9dccec",
      beneficiary_colour_zero: "#eee",

      region_colour_default: interpolateYlGn(0),
    };
  },

  methods: {
    tooltipTemplate(d) {
      const allocation = d.allocation || 0;
      let region_name;
      let extra = "";
      if (d.id.length == 2) {
        region_name = this.COUNTRIES[d.id].name;
        extra = `
            <li>${ this.currency(d.allocation || 0) }</li>
            `
      } else {
        region_name = this.get_nuts_label(d.id) + '(' + d.id + ')';
      }

      return `
          <div class="title-container">
            <svg>
              <use xlink:href="#${this.get_flag_name(d.id)}" />
            </svg>
            <span class="name">${ region_name }</span>
          </div>
          <ul>
            ${ extra }
            <li>${d.sectors.size()} `+  this.singularize(`sectors`, d.sectors.size()) + `</li>
            <li>${d.areas.size()} `+  this.singularize(`programme areas`, d.areas.size()) + `</li>
            <li>${d.programmes.size()}  `+  this.singularize(`programmes`, d.programmes.size()) + `</li>
          </ul>
      `;
    },

    renderData(t) {
      if (t === undefined) t = this.getTransition();
      const dataset = d3.values(this.data);

      const beneficiaries = this.chart.selectAll('.states > g.beneficiary')
                                .data(dataset, (d) => d.id );

      beneficiaries
        .classed("zero", false)
        .select("path")
        .transition(t)
        .attr("fill", this.beneficiary_colour_default);

      beneficiaries
        .exit()
        .classed("zero", true)
        .each(function() {
          // make that value 0 too. totally mean.
          Object.assign(d3.select(this).datum(), {
            allocation: 0,
            sectors: [],
          });
        })
        .select("path")
        .transition(t)
        .attr("fill", this.beneficiary_colour_zero);

      // and TODO: disable filtering for 0 / missing items
    },

    renderRegionData(state, regiondata, t) {
      if (t === undefined) t = this.getTransition();

      const values = regiondata.map( (x) => x.allocation ),
            max = Math.max(...values),
            min = Math.min(...values.filter( (x) => x != 0 ));

      // d3's chromatic scales take a [0, 1] domain
      // TODO: user testing. linear or log?
      //const x = d3.scaleLinear()
      const x = d3.scaleLog()
                  .domain([min, max])
                  .range([.1, 1]);

      const regions = this.chart
                          .select(`g.regions > g.state.${state} > g.layer`)
                          .selectAll('g')
                          .data(regiondata, (d) => d.id );

      // protect against data that has unknown NUTS codes
      const _badregions = regions.enter().data();
      if (_badregions.length)
        // TODO: log this in production
        //throw new Error(
        console.error(
          "Unknown NUTS codes: " +
          _badregions.map( (d) => d.id ).join(", ")
        );

      regions.select("path")
        .transition(t)
        .attr("fill", (d) => interpolateYlGn(x(d.allocation)) );

      regions.exit().select("path")
             .transition(t)
             .attr("fill", interpolateYlGn(0));
      // TODO: and reset data to 0 ?
    },
  },
});
</script>
