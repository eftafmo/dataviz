<script>
import * as d3 from 'd3';
import {interpolateYlGn} from 'd3-scale-chromatic';

import BaseMap from './BaseMap';


export default BaseMap.extend({
  data() {
    return {
      default_region_colour: interpolateYlGn(0),
    };
  },

  methods: {
    tooltipTemplate(d) {
      if (d.id.length == 2)
        return `
          <div class="title-container">
            <img src="/assets/imgs/${ this.get_flag_name(d.id) }.png" />
            <span class="name">${ this.COUNTRIES[d.id].name }</span>
          </div>
          ${ this.currency(d.total || 0) }
        `;
      else
        return `
          <div class="title-container">
            <span class="name">${ this.region_names[d.id] } (${d.id})</span>
          </div>
          ${ this.currency(d.allocation || 0) }
          <small>(Temporary)<small>
        `;
    },

    renderData() {
      const t = this.getTransition();
      const beneficiarydata = d3.values(this.beneficiarydata);
      const beneficiaries = this.chart.selectAll('.states > g.beneficiary')
                                .data(beneficiarydata, (d) => d.id );

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
            allocation: {},
            sectors: [],
            total: 0,
          });
        })
        .select("path")
        .transition(t)
        .attr("fill", this.beneficiary_colour_zero);

      // and TODO: disable filtering for 0 / missing items
    },

    _renderRegionData(state, regiondata, t) {
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

      const regions = this.chart.select('g.regions > g.state.' + state)
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
