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
    renderData() {
      const t = this.getTransition();
      const beneficiarydata = d3.values(this.beneficiarydata);
      const states = this.chart.select('.states').selectAll('path'),
            beneficiaries = states.filter(this.isBeneficiary)
                                  .data(beneficiarydata, (d) => d.id );

      beneficiaries
        .classed("zero", false)
        .transition(t)
        .attr("fill", this.beneficiary_colour.default);

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
        .transition(t)
        .attr("fill", this.beneficiary_colour.zero);

      // and TODO: disable filtering for 0 / missing items
    },

    renderRegionData(t) {
      const state = this.filters.beneficiary;

      // this could be called by another filter.
      // bail out if no beneficiary selected.
      if (state === null) return;

      let dataset = this._region_data[state];

      // placing the rendering code inside a function,
      // because the dataset might not be loaded yet
      const _renderRegionData = () => {
        const _filters = d3.keys(this.filters).filter( (f) => f != 'beneficiary' );
        const regiondata = this.filter(dataset, _filters);

        const totals = {},
              // another version of the above, but storing only id -> value
              _totals = {};
        let max = 0;

        for (const row of regiondata) {
          const id = row.id;
          let item = totals[id];
          if (item === undefined) {
            item = totals[id] = {
              id: id,
              amount: 0,
            };
          }

          item.amount += +row.amount;

          // save another iteration and track the max
          max = Math.max(item.amount, max);
          // save this too, we'll use it to get the min
          _totals[id] = item.amount;
        }
        const min = d3.min(d3.values(_totals));

        // d3's chromatic scales take a [0, 1] domain
        // TODO: user testing. linear or log?
        //const x = d3.scaleLinear()
        const x = d3.scaleLog()
                    .domain([min, max])
                    .range([.1, 1]);

        if (t === undefined) t = this.getTransition();
        const regions = this.chart.select('g.regions > g.' + state)
                            .selectAll('path').data(d3.values(totals), (d) => d.id );

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
               .attr("fill", (d) => interpolateYlGn(x(d.amount)) );

        regions.exit()
               .transition(t)
               .attr("fill", interpolateYlGn(0));
               // TODO: and reset data to 0 ?
      };

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
          _renderRegionData();
        } );
      } else {
        _renderRegionData();
      }
    },
  },
});
</script>
