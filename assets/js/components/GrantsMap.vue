<style lang="less">
.dataviz .viz.map.allocation.grants {
  .legend {
    .square {
      &.amount {
        width: 160px;
        background: #fcf5c4; /* Old browsers */
        background: linear-gradient(to right, #fcf5c4 0%,#fcf5c4 25%,#278b33 60%,#036121 100%); /* W3C, IE10+, FF16+, Chrome26+, Opera12+, Safari7+ */
      }
    }
  }
}
</style>


<script>
import * as d3 from 'd3';
import {interpolateYlGn} from 'd3-scale-chromatic';

import AllocationMap from './AllocationMap'


export default {
  extends: AllocationMap,
  type: "grants",

  data() {
    return {
      nuts_level: 3,
      draw_nuts_levels: [3],

      region_colour: interpolateYlGn(0),
    }
  },

  methods: {
    tooltipTemplate(d) {
      const allocation = d.allocation || 0,
            country_is_donor = d.id.length === 2 && this.COUNTRIES[d.id].type === "donor",
            state_type = country_is_donor ? 'donor-tooltip' : '';

      let region_name;
      let extra = "";
      if (d.id.length == 2) {
        region_name = this.COUNTRIES[d.id].name;
        extra = `
            <li>${ this.currency(allocation) }</li>
            `
      } else {
        region_name = this.getRegionName(d.id) + '(' + d.id + ')';
      }

      // get a set's amount
      const get_amount = s => (s === undefined) ? 0 : s.size(),
            country_details = country_is_donor ? '' : `
              <ul>
                ${ extra }
                <li>${ get_amount(d.sectors) } `+  this.singularize(`sectors`, get_amount(d.sectors)) + `</li>
                <li>${ get_amount(d.areas) } `+  this.singularize(`programme areas`, get_amount(d.areas)) + `</li>
                <li>${ get_amount(d.programmes) }  `+  this.singularize(`programmes`, get_amount(d.programmes) ) + `</li>
              </ul>
            `;

      return `
        <div class="title-container ${state_type}">
          <svg>
            <use xlink:href="#${this.get_flag_name(d.id)}" />
          </svg>
          <span class="name">${ region_name }</span>
        </div>` + country_details;
    },

    _domouse(over, d, i, group) {
      const self = this.$super._domouse(over, d, i, group)
      if (!self) return

      if (this.hovered_region_colour &&
          d.id.length == 2 &&
          d.allocation != 0 &&
          this.COUNTRIES[d.id].type === "beneficiary"
      )
        self
          .transition(this.getTransition(this.short_duration))
          .attr("fill", over ? this.hovered_region_colour :
                               this.fillfunc)
    },

    renderData(t) {
      if (t === undefined) t = this.getTransition();
      const dataset = Object.values(this.data);

      const beneficiaries = this.chart.selectAll('.regions > .level0 > path.beneficiary')
                                .data(dataset, (d) => d.id );

      beneficiaries
        .classed("zero", false)
        .transition(t)
        .attr("fill", this.beneficiary_colour)

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

    renderRegionData(region, regiondata, t) {
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
                          .selectAll(`g.regions > g.${region} > path`)
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
}
</script>
