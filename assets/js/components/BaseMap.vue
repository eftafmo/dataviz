<template>
<div :class="[$options.type, { rendering: !rendered }]">
  <slot name="title" v-if="!this.embedded"></slot>
  <dropdown v-if="hasData" filter="beneficiary" title="No filter selected" :items="data"></dropdown>

  <svg class="defs">
    <defs>
      <pattern id="multi-fm" width="50" height="11" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="50" height="6"
              class="norway-grants"
              :fill="fmcolour('norway-grants')"
              :stroke="fmcolour('norway-grants')"
        />
        <rect x="0" y="6" width="50" height="5"
              class="eea-grants"
              :fill="fmcolour('eea-grants')"
              :stroke="fmcolour('eea-grants')"
        />
      </pattern>
    </defs>
  </svg>

  <map-base
      ref="map"
      v-on:rendered="mapRendered"
      :origin="origin"
      :default_nuts_levels="draw_nuts_levels"
      :donor_colour="fmcolour('eea-grants')"
      norway_colour="url(#multi-fm)"
      :beneficiary_colour="beneficiary_colour_default"
      :region_colour="region_colour_default"
  >
    <transition appear name="fade">
      <nuts-selector
          v-if="show_nuts_selector"
          :levels="draw_nuts_levels"
          v-model="nuts_level"
      ></nuts-selector>
    </transition>
  </map-base>

  <div class="legend" v-if="rendered">
    <ul class="legend-items">
      <li v-if="!(filters.beneficiary && $options.type == 'viz map allocation grants')">
        <svg class="square" v-if="rendered" height="20" width="20">
          <rect height="20" width="20" fill="url(#multi-fm)"/>
        </svg>
        Donor state(s)
      </li>
      <li v-if="!(filters.beneficiary && $options.type == 'viz map allocation grants')">
        <span class="square"></span>
        Beneficiary states
      </li>
      <li v-if="filters.beneficiary && $options.type == 'viz map allocation grants'">
      <span class="square amount"></span>
        Project grants
      </li>
    </ul>
  </div>

</div>
</template>

<style lang="less">
.viz.map.allocation {
  @beneficiary: #ddd;

  .hovered {
    stroke: #005494;
  }

  .chart {
    .transitioning {
      pointer-events: none;
    }

    .states {
      .beneficiary {
        cursor: pointer;
        pointer-events: visible; // noIE<=10

        &.zero {
          cursor: not-allowed;
        }

        &:not(.zero):hover path {
          .hovered;
        }
      }
    }

    .regions {
      pointer-events: visible;

      path {
        &:hover {
          //.hovered;
          stroke: black;
        }
      }
    }
  }

  svg.defs {
    height: 0;
    width: 0;
    position: fixed;
    top: 0;
    left: 0;
    opacity: 0;
  }
  .nuts-selector {
    position: absolute;
    top: 10px;
    right: 10px;
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
import {slugify} from 'js/lib/util';

import Chart from './Chart';

import MapMixin from './mixins/Map';
import WithCountriesMixin from './mixins/WithCountries';
import WithFMsMixin from './mixins/WithFMs';
import WithTooltipMixin from './mixins/WithTooltip';
import WithNUTSMixin from './mixins/WithNUTS';

import NutsSelector from './includes/NutsSelector';


export default Chart.extend({
  type: "allocation",

  mixins: [
    MapMixin,
    WithCountriesMixin, WithFMsMixin,
    WithTooltipMixin,
    WithNUTSMixin,
  ],

  components: {
    "nuts-selector": NutsSelector,
  },

  props: {
    // this is a "template" with the string 'XX' meant to be replaced
    // with the country code
    detailsDatasource: String,
  },

  data() {
    return {
      donor_colour_inactive: "#fff",

      beneficiary_colour_default: "none",
      beneficiary_colour_hovered: null,
      beneficiary_colour_zero: "none",

      region_colour_default: "none",

      draw_nuts_levels: [1, 2, 3],
      nuts_level: 3, // the startling nuts level
    };
  },

  created() {
    // don't filter / aggregate by beneficiary, group by it
    // (TODO: this smells like a pattern already)
    let idx;

    idx = this.filter_by.indexOf("beneficiary");
    if (idx !== -1)
      this.filter_by.splice(idx, 1);

    this.aggregate_by.push(
        { source: "beneficiary", destination: "id" }
    );

    idx = this.aggregate_on.findIndex(x => x.source == "beneficiary");
    if (idx !== -1) this.aggregate_on.splice(idx, 1);

    // cache for region-level data
    this._region_data = {};
  },

  computed: {
    show_nuts_selector() {
      return !!(this.draw_nuts_levels.length > 1 &&
                this.filters.beneficiary);
    },

    data() {
      const aggregated = d3.values(this.aggregated);

      for (const item of aggregated) {
        item.name = this.BENEFICIARIES[item.id].name;
      }
      return aggregated.sort((a, b) => d3.ascending(a.name, b.name));
    },
  },

  methods: {
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

    stateEnter(d, i, group) {
      // disable map zoom and tooltips on donor states #291
      if (this.isDonor(d)) { return };
      const this_ = group[i];

      d3.select(this_).raise();
      this.tip.show.call(this_, d, i, group);
    },

    stateLeave(d, i, group) {
      // disable map zoom and tooltips on donor states #291
      if (this.isDonor(d)) { return };
      const this_ = group[i];

      this.tip.hide(this_, d, i, group);
    },

    stateClick(d, i, group) {
      // disable map zoom and tooltips on donor states #291
      if (this.isDonor(d)) { return };
      const this_ = group[i];

      this.toggleBeneficiary(d, this_);
    },

    render(initial) {
      // this initial stuff copy-pasted
      if (initial) this.chart_rendered = false;

      this.renderData();
      if (this.filters.beneficiary)
        this.handleFilterBeneficiary(this.filters.beneficiary);

      this.chart_rendered = true;
    },

    renderData(t) {
      throw new Error("Not implemented");
    },

    renderRegionData(state, regiondata, t) {
      throw new Error("Not implemented");
    },

    doRenderRegionData(t) {
      const state = this.filters.beneficiary;

      // this could be called by another filter.
      // bail out if no beneficiary selected.
      if (state === null) return;

      let dataset = this._region_data[state];

      if (dataset === undefined) {
        // reset the transition, data might arrive too late to use it.
        // TODO: run a throbber / suggest data loading somehow?
        t = undefined;

        // fetch the data, fill the cache, render
        const url = this.detailsDatasource.replace('XX', state);

        d3.json(url, (error, data) => {
          if (error) throw error;
          dataset = this._region_data[state] = data;
          this.renderRegionData(state, this.computeRegionData(dataset), t);
        } );
      } else {
        this.renderRegionData(state, this.computeRegionData(dataset), t);
      }
    },

    computeRegionData(regiondataset) {
      const filtered = this.filter(regiondataset, this.filter_by);
      return this.aggregate(filtered, ['id'], this.aggregate_on, true);
    },

    showNutsLevel(lvl, yes, t) {
      if (t === undefined) t = this.getTransition();

      // we could bother to not transition invisible stuff... but... oh well
      const containers = this.chart
        .select(".regions").selectAll("g.state > g.layer.level" + lvl)
        .style("display", null)
        .classed("transitioning", true)
        .transition(t)
        .attr("opacity", Number(yes))
        .on("end", function() {
          d3.select(this)
            .style("display", yes ? null : "none")
            .classed("transitioning", false);
        });
    },

    registerEvents(selection) {
      const $this = this;

      const doMouse = (over) => {
        return function(d, i) {
          const sel = d3.select(this);

          if (over) {
            sel.raise();
            $this.tip.show.call(this, d, i);
          } else {
            $this.tip.hide.call(this, d, i);
          }

          if ($this.beneficiary_colour_hovered &&
              d.id.length == 2 &&
              d.allocation != 0
          )
            sel.select("path")
               .transition($this.getTransition($this.short_duration))
               .attr("fill", over ? $this.beneficiary_colour_hovered :
                                    $this.beneficiary_colour_default);
        }
      };

      selection
        .on("click", function (d) {
          if (d.id.length == 2)
            $this.toggleBeneficiary(d, this);
        })
        .on("mouseenter", doMouse(true))
        .on("mouseleave", doMouse(false));
    },

    handleFilterBeneficiary(newid, oldid) {
      const $this = this;
      const t = this.getTransition();

      if (newid) {
        const regions = this.map.renderRegions(newid);
        // map.renderRegions() only returns the newly rendered selection
        if (regions) {
          this.registerEvents(regions);

          // enable the current nuts layer. cheat a bit, because
          // the layers are this selection's parents
          d3.selectAll(regions._parents)
            .filter(d => d.level == this.nuts_level)
            .style("display", null)
            .attr("opacity", 1);
        }
      }

      // fade in old state layer / out old regions layer
      if (oldid) {
        this.chart.select('.states > g.beneficiary.' + oldid)
            .transition(t)
            .attr("opacity", 1);

        this.chart.select('.regions > g.state.' + oldid)
            .classed("transitioning", true)
            .transition(t)
            .attr("opacity", 0)
            .on("end", function() {
              d3.select(this)
                .style("display", "none")
                .classed("transitioning", false)
                // also reset regions to default colour
                .selectAll("path")
                .attr("fill", $this.region_colour_default);
            });
      }

      // fade out new state layer / in new regions layer
      if (newid) {
        this.chart.select('.states > g.beneficiary.' + newid)
            .transition(t)
            .attr("opacity", 0);

        this.chart.select('.regions > g.state.' + newid)
            .classed("transitioning", true)
            .style("display", null)
            .transition(t)
            .attr("opacity", 1)
            .on("end", function() {
              d3.select(this)
                .classed("transitioning", false);
            });
      }

      // zoom to the new thing (or out of the old)
      this.map.zoomTo(newid, t);

      // and ...
      this.doRenderRegionData(t);

      // and also, because
      this.tip.hide()
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
        .filter( (d) => this.isDonor(d) && d.id != "NO" )
        .transition(t)
        .attr("fill", colourfuncEEA);

      // Norway uses a pattern fill
      d3.select(this.$el).select("svg > defs > pattern#multi-fm").selectAll("rect")
        .datum(function() { return this.getAttribute("class"); })
        .transition(t)
        .attr("fill", colourfuncNO)
        .attr("stroke", colourfuncNO);

      /*
       * part 2: change the region data
       */

      this.doRenderRegionData(t);
    },

    handleFilter(type, val, old) {
      const t = this.getTransition();
      this.renderData(t);
      this.doRenderRegionData(t);
    },
  },

  watch: {
    map_rendered() {
      this.chart.select("g.states").selectAll("g.beneficiary")
          .call(this.registerEvents);
    },

    nuts_level(lvl, old) {
      const t = this.getTransition();

      this.showNutsLevel(old, false, t);
      this.showNutsLevel(lvl, true, t);
    },
  },

});
</script>
