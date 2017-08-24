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
    }
  },

  methods: {
    tooltipTemplate(d) {
      const allocation = d.allocation || 0;
      let region_name;
      let extra = "";
      if (d.id.length == 2) {
        region_name = this.COUNTRIES[d.id].name;
        extra = `
            <li>${ this.currency(allocation) }</li>
            `
      } else {
        region_name = this.get_nuts_label(d.id) + '(' + d.id + ')';
      }

      // get a set's amount
      const get_amount = s => (s === undefined) ? 0 : s.size()

      return `
          <div class="title-container">
            <svg>
              <use xlink:href="#${this.get_flag_name(d.id)}" />
            </svg>
            <span class="name">${ region_name }</span>
          </div>
          <ul>
            ${ extra }
            <li>${ get_amount(d.sectors) } `+  this.singularize(`sectors`, get_amount(d.sectors)) + `</li>
            <li>${ get_amount(d.areas) } `+  this.singularize(`programme areas`, get_amount(d.areas)) + `</li>
            <li>${ get_amount(d.programmes) }  `+  this.singularize(`programmes`, get_amount(d.programmes) ) + `</li>
          </ul>
      `;
    },

    renderData(t) {
      if (t === undefined) t = this.getTransition();
      const dataset = d3.values(this.data);

      const beneficiaries = this.chart.selectAll('.regions > .level0 > path.beneficiary')
                                .data(dataset, (d) => d.id );

      beneficiaries
        .classed("zero", false)
        .transition(t)
        .attr("fill", this.beneficiary_colour_default)

      beneficiaries
        .exit()
        .classed("zero", true)
        .each(function(d) {
          // reset data in a nice, hardcoded way
          Object.assign(d, {
            allocation: 0,
          })
        })
        .transition(t)
        .attr("fill", this.beneficiary_colour_zero)

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
                          .selectAll(`g.regions > g.${state} > path`)
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

      regions
        .transition(t)
        .attr("fill", d => interpolateYlGn(x(d.allocation)) )

      regions.exit()
        .transition(t)
        .attr("fill", interpolateYlGn(0))
      // TODO: and reset data to 0 ?
    },
  },
});
</script>
