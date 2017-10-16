<template>
<div :class="classNames">
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
    <template slot="after-map">
      <region-details
          :region="current_region_data"
      ></region-details>

      <transition appear name="fade">
        <div class="toolbox" v-if="current_region">
          <a title="zoom out"
             @click="zoomOut()"
          ><span class="icon-cross"></span></a>
        </div>
      </transition>
    </template>
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
.dataviz .viz.map.allocation {
  @beneficiary: #ddd;

  .chart{
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

  .toolbox {
    position: absolute;
    right: 1em;
    top: 1em;

    font-weight: bold;

    * {
      display: block;
    }

    a {
      cursor: pointer;
      padding: .4em;
      color: #666;
      background-color: rgba(238, 238, 238, .7);
      text-decoration: none;
      opacity: .7;

      &:hover {
        color: #3d90f3;
        background-color: #eee;
        opacity: 1;
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
import WithRegionsMixin from './mixins/WithRegions';


export default Chart.extend({
  type: "allocation",

  mixins: [
    MapMixin,
    WithCountriesMixin, WithFMsMixin,
    WithTooltipMixin,
    WithNUTSMixin,
    WithRegionsMixin,
  ],

  components: {
    regionDetails: { render(c) { return c() } },
  },

  props: {
    // this is a "template" with the string 'XX' meant to be replaced
    // with the country code
    detailsDatasource: String,
  },

  data() {
    return {
      donor_colour_inactive: "#fff",

      beneficiary_colour: "none",
      region_colour: "none",

      zoomed_nuts_level: 3,

      all_nuts_levels: [0, 3],
      // restrict rendering to donors and beneficiaries
      all_states: Object.keys(this.COUNTRIES).filter(
        id => (
          ["donor", "beneficiary"].indexOf(this.COUNTRIES[id].type) !== -1 &&
          id != "Intl" // let's not forget about that :)
        )
      ),

      current_region: null,
      hovered_region: null,

      current_region_data: null,
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

    // cache for raw region-level data
    this._region_data = {} // raw

    // if it's a standalone country we'll need some custom logic
    this.is_standalone = !!(this.embedded && this.filters.beneficiary)

    // these ones are used to unify beneficiary / region handling
    this.current_region = this.filters.beneficiary
    this._prev_region = null
  },

  computed: {
    initial_regions() {
      if (this.is_standalone)
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
    getParentRegion(id) {
      if (!id) return

      const level = this.getRegionLevel(id)
      if (level == 0)
        return null // for consistency with filter values
      if (level == this.zoomed_nuts_level)
        return id.substr(0, 2)
      return id.substr(0, id.length - 1)
    },

    zoomOut() {
      this.filters.beneficiary = null
    },

    tooltipTemplate() {
      throw new Error("Not implemented");
    },

    createTooltip() {
      let tip = d3.tip()
          .attr('class', 'dataviz-tooltip map')
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
        return this.beneficiary_colour

      return this.region_colour
    },

    opacityfunc(parentid) {
      return parentid == "" ? 1 : 0
    },

    renderChart() {
      const t = this.getTransition()

      this.renderDonorColours(t)
      this.doZoom(t)
      this.renderData(t)
      this.doRenderRegionData(t) // leave this last in the chain, because...

      // ... this should normally be updated at this point,
      // but renderRegionData will be called async the first time,
      // so doing it there
      //this._prev_region = this.current_region
    },

    renderData(t) {
      throw new Error("Not implemented");
    },

    renderRegionData(region, regiondata, t) {
      throw new Error("Not implemented");
    },

    doRenderRegionData(t) {
      const region = this.current_region
      if (region === null) {
        // nothing to do, but don't forget to reset the prev region
        this._prev_region = this.current_region
        return
      }

      const state = region.substr(0, 2)

      let dataset = this._region_data[state];

      const renderRegionData = (dataset, t) => {
        // we want to "render" the data for all ancestors of the given region.
        // (the local implementation will decide what rendering actually means)
        let r = region
        while(r) {
          this.renderRegionData(r, this.computeRegionData(dataset), t)
          r = this.getParentRegion(r)
        }

        this._prev_region = this.current_region
      }

      if (dataset === undefined) {
        // data might arrive too late to use the transition,
        // so prepare to reset it if necessary
        let t_expired = false
        const t_duration = t.duration() // so we can replicate a similar transition
        t.on("end", () => t_expired = true)
        // TODO: run a throbber / suggest data loading somehow?

        // fetch the data, fill the cache, render
        const url = this.detailsDatasource.replace('XX', state);

        d3.json(url, (error, data) => {
          if (error) throw error;

          dataset = this._region_data[state] = data;
          if(t_expired) t = this.getTransition(t_duration)
          renderRegionData(dataset, t)
        } );
      } else {
        renderRegionData(dataset, t)
      }
    },

    computeRegionData(regiondataset) {
      const filtered = this.filter(regiondataset, this.filter_by)
      return this.aggregate(filtered, ['id'], this.aggregate_on, true)
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

    _domouse(over, d, i, group) {
      // disable mouseover events while transitioning
      if (this.transitioning) return

      const self = d3.select(group[i])

      // also disable when zeroed
      if (self.classed("zero")) return

      if (over) {
        self.raise()
        // we also need to raise the parent container
        d3.select(this.parentNode).raise()

        this.tip.show.call(self.node(), d, i)
        this.hovered_region = d
      } else {
        this.tip.hide.call(self.node(), d, i)
        this.hovered_region = null
      }

      return self
    },

    mouseenterfunc(d, i, group) {
      return this._domouse(true, d, i, group)
    },

    mouseleavefunc(d, i, group) {
      return this._domouse(false, d, i, group)
    },

    clickfunc(d, i, group) {
      if(d.id.length === 2 && this.COUNTRIES[d.id].type !== "beneficiary") return;

      const self = d3.select(group[i])
      if (self.classed("zero")) return

      if (d.id.length == 2) this.toggleBeneficiary(d)

      return self
    },

    registerEvents(selection) {
      selection
        .on("click", this.clickfunc)
        .on("mouseenter", this.mouseenterfunc)
        .on("mouseleave", this.mouseleavefunc)
    },

    doZoom(t) {
      const newid = this.current_region,
            oldid = this._prev_region;

      if (newid == oldid) return

      const $this = this

      const _showchildren = (id, yes) => {
        // only select the exact region when showing,
        // otherwise hide all descendant regions
        let selector = `.regions > .${id}`
        if (yes) {
          const level = id.length == 2 ? this.zoomed_nuts_level
                                       : id.length - 2 + 1
          selector += `.level${level}`
        }

        const parent = this.chart.selectAll(selector)
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
              .attr("fill", $this.region_colour)
          })
      }

      const _showregion = (id, yes) => {
        const level = id.length == 2 ? 0 : id.length - 2

        const region = this.chart.select(`.regions > .level${level}`)
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
        // hide the selected region, show its children
        _showregion(newid, false)
        _showchildren(newid, true)
      }

      if (oldid) {
        // show the old region
        _showregion(oldid, true)
        // hide old region unless it's an ancestor
        if (!newid || oldid != newid.substr(0, oldid.length)) {
          // find the topmost ancestor of the previous region
          // that isn't the new one or the new one's parent
          const common = newid ? this.getParentRegion(newid) : newid
          let prev = oldid

          while (true) {
            const p = this.getParentRegion(prev)
            if (p == newid || p == common) break
            else prev = p
          }

          _showchildren(prev, false)
        }
      }

      this.map.zoomTo(newid, t)
    },

    handleFilterBeneficiary(v) {
      this.current_region = v
      if (v) this.map.renderRegions(v, this.zoomed_nuts_level)
      if (!v) this.current_region_data = null
      this.tip.hide()
      this.render()
    },
  },
});
</script>
