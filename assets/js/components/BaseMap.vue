<template>
<div :class="[$options.type, { rendering: !rendered }]">
  <slot name="title" v-if="!this.embedded"></slot>
  <dropdown v-if="hasData" filter="beneficiary" title="No filter selected" :items="data"></dropdown>

  <svg class="defs" ref="defs">
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
      @rendered="handleMapRendered"
      @regions-rendered="registerEvents"
      :origin="origin"
      :initial_regions="initial_regions"
      :all_states="all_states"
      :all_levels="all_nuts_levels"
      :fillfunc="fillfunc"
      :opacityfunc="opacityfunc"
  >

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

  .chart {
    .transitioning {
      pointer-events: none;
    }

    .regions {
      .beneficiary:not(.zero) {
        &:hover {
          stroke: #000;
        }
      }
      .level0 .beneficiary{
        &:not(.zero) {
          cursor: pointer;

          &:hover {
            stroke: #005494;
          }
        }

        &.zero {
          cursor: not-allowed;
          //pointer-events: none;
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


export default Chart.extend({
  type: "allocation",

  mixins: [
    MapMixin,
    WithCountriesMixin, WithFMsMixin,
    WithTooltipMixin,
    WithNUTSMixin,
  ],

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

      zoomed_nuts_level: 3,

      all_nuts_levels: [0, 3],
      // restrict rendering to donors and beneficiaries
      all_states: Object.keys(this.COUNTRIES).filter(
        id => (
          ["donor", "beneficiary"].indexOf(this.COUNTRIES[id].type) !== -1 &&
          id != "Intl" // let's not forget about that :)
        )
      ),
    }
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

    // aggreggate on fm, we'll need that for donor colours
    this.aggregate_on.push(
      { source: "fm", destination: "fms", type: String }
    )

    // cache for region-level data
    this._region_data = {};

    // we'll need this for custom logic
    this.is_single_country = !!(this.embedded && this.filters.beneficiary)

    // this one's used to keep zooming code away from handleFilterBeneficiary
    this._prev_beneficiary = null
  },

  computed: {
    initial_regions() {
      if (this.is_single_country)
        return [{
          states: this.filters.beneficiary,
          levels: [0, this.zoomed_nuts_level],
        }]

      // otherwise, we always want level0 stuff, even when ready-zoomed
      const initials = [ { levels: 0 } ]

      if (this.filters.beneficiary)
        initials.push({
          states: this.filters.beneficiary,
          levels: this.zoomed_nuts_level,
        })

      return initials
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

    fillfunc(d) {
      const id = d.id,
            level = id.length - 2,
            country = id.substr(0, 2),
            type = this.COUNTRIES[country].type;

      if (type == "donor") {
        if (country == "NO")
          return "url(#multi-fm)"

        if (this.filters.fm == "Norway Grants")
          return this.donor_colour_inactive

        return this.fmcolour("eea-grants")
      }

      if (level == 0)
        return this.beneficiary_colour_default

      return this.region_colour_default
    },

    opacityfunc(parentid) {
      return parentid == "" ? 1 : 0
    },

    render(initial) {
      // this "initial" stuff copy-pasted
      if (initial) this.chart_rendered = false;

      const t = this.getTransition()

      this.renderData(t)
      this.renderDonorColours(t)
      this.doRenderRegionData(t)
      this.doZoom(t)

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
      // bail out if no beneficiary selected.
      if (state === null) return;

      let dataset = this._region_data[state];

      if (dataset === undefined) {
        // data might arrive too late to use the transition,
        // so prepare to reset it if necessary
        let t_expired = false
        // TODO: handle the case when t.duration() == 0
        // to avoid the initial transition when pre-filtered
        t.on("end", () => t_expired = true)
        // TODO: run a throbber / suggest data loading somehow?

        // fetch the data, fill the cache, render
        const url = this.detailsDatasource.replace('XX', state);

        d3.json(url, (error, data) => {
          if (error) throw error;

          dataset = this._region_data[state] = data;
          if(t_expired) t = undefined
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

    renderDonorColours(t) {
      let with_eea = false,
          with_no = false;

      const eea = this.FMS["eea-grants"].name,
            no = this.FMS["norway-grants"].name;

      const fmfilter = this.filters.fm

      if (fmfilter == eea)
        with_eea = true

      else if (fmfilter == no)
        with_no = true

      else {
        // the dataset is the source of truth
        for (const row of this.data) {
          if (row.fms.has(eea))
            with_eea = true

          if (row.fms.has(no))
            with_no = true

          if (with_eea && with_no) break
        }
      }

      // EEA donors are either coloured or inactive
      this.chart.select(".regions .level0").selectAll("path.donor")
        .filter(d => d.id != "NO")
        .transition(t)
        .attr("fill",
              with_eea ? this.fmcolour("eea-grants") :
                         this.donor_colour_inactive
        )

      // Norway donors are handled via the pattern fill
      const colourfuncNO = id => {
        if (with_eea && with_no) return this.fmcolour(id)

        if (with_eea) return this.fmcolour("eea-grants")
        if (with_no) return this.fmcolour("norway-grants")
      }

      d3.select(this.$refs.defs).selectAll("pattern#multi-fm rect")
        .datum(function() { return this.getAttribute("class") })
        .transition(t)
        .attr("fill", colourfuncNO)
        .attr("stroke", colourfuncNO)
    },

    registerEvents(selection) {
      const $this = this;

      const doMouse = (over) => {
        return function(d, i) {
          // disable mouseover events while transitioning
          if ($this.transitioning) return

          const self = d3.select(this);

          // disable also when zeroed
          if (self.classed("zero")) return

          if (over) {
            self.raise()
            // we also need to raise the parent container
            d3.select(this.parentNode).raise()

            $this.tip.show.call(this, d, i);
          } else {
            $this.tip.hide.call(this, d, i);
          }

          if ($this.beneficiary_colour_hovered &&
              d.id.length == 2 &&
              d.allocation != 0
          )
            self
            .transition($this.getTransition($this.short_duration))
            .attr("fill", over ? $this.beneficiary_colour_hovered :
                                 $this.beneficiary_colour_default)
        }
      };

      selection
        // only beneficiaries have events
        .filter(d => d.id.length != 2 || this.COUNTRIES[d.id].type === "beneficiary")
        .on("click", function(d) {
          if (d3.select(this).classed("zero")) return

          if (d.id.length == 2) {
            $this.toggleBeneficiary(d)
          }
        })
        .on("mouseenter", doMouse(true))
        .on("mouseleave", doMouse(false))
    },

    doZoom(t) {
      const newid = this.filters.beneficiary,
            oldid = this._prev_beneficiary;

      if (newid == oldid) return

      const $this = this

      const _showregions = (id, yes) => {
        const regions = this.chart.selectAll(
            `.regions > .${id}.level${this.zoomed_nuts_level}`
          )
          //.raise()
          .classed("transitioning", true)
          .style("display", null)
          .transition(t)
          .attr("opacity", Number(yes))
          .on("end", function() {
            const s = d3.select(this)
              .classed("transitioning", false)

            if (!yes) s
              .style("display", "none")
              // also reset regions to default colour
              .selectAll("path")
              .attr("fill", $this.region_colour_default)
          })
      }

      const _showstate = (id, yes) => {
        const state = this.chart.select(".regions > .level0")
          //.lower()
          .selectAll(`.${id}`) // must selectAll, or else data goes poof
          .style("display", null)
          .transition(t)
          .attr("opacity", Number(yes))

          .on("start", function() {
            $this.transitioning = true
          })
          .on("end", function() {
            $this.transitioning = false
            if (!yes)
              d3.select(this).style("display", "none")
          })
          .on("interrupt", function(d) {
            // watch out for the impossible "double interrupt":
            // a previous country was supposed to be faded back in,
            // but that got interrupted too
            // (that's a real fast triple click in at least 2 different places)
            if (oldid && oldid != d.id && !yes) {
              $this.chart.select(".regions > .level0").selectAll(`.${oldid}`)
                .attr("opacity", 1)
            }
          })
      }

      if (newid) {
        _showregions(newid, true)
        _showstate(newid, false)
      }

      if (oldid) {
        _showregions(oldid, false)
        _showstate(oldid, true)
      }

      this.map.zoomTo(newid, t)
      this._prev_beneficiary = newid
    },

    handleFilterBeneficiary(v) {
      if (v) this.map.renderRegions(v, this.zoomed_nuts_level)
      this.tip.hide()
      this.render()
    },
  },
});
</script>
