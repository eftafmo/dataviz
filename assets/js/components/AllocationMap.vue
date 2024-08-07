<template>
  <div :class="classNames">
    <slot v-if="!embedded" name="title"></slot>
    <dropdown
      v-if="hasData"
      filter="beneficiary"
      title="No filter selected"
      :items="dropDownItems"
    ></dropdown>

    <map-base
      ref="map"
      :period="period"
      :initial-regions="initial_regions"
      :all-states="all_states"
      :all-levels="all_nuts_levels"
      :fillfunc="fillfunc"
      :opacityfunc="opacityfunc"
      @rendered="handleMapRendered"
      @regions-rendered="registerEvents"
    >
      <template #default>
        <pijama-defs ref="defs"></pijama-defs>
      </template>
      <template #after-map>
        <region-details :region="current_region_data"></region-details>

        <transition appear name="fade">
          <div v-if="current_region" class="toolbox">
            <a title="zoom out" @click="zoomOut()"
              ><span class="icon-cross"></span
            ></a>
          </div>
        </transition>
      </template>
    </map-base>

    <div v-if="rendered" class="legend">
      <ul class="legend-items">
        <li
          v-if="
            !(
              filters.beneficiary &&
              $options.type == 'viz map allocation grants'
            )
          "
        >
          <svg v-if="rendered" class="square" height="20" width="20">
            <rect height="20" width="20" fill="url(#multi-fm)" />
          </svg>
          Donor State(s)
        </li>
        <li
          v-if="
            !(
              filters.beneficiary &&
              $options.type == 'viz map allocation grants'
            )
          "
        >
          <span class="square"></span>
          Beneficiary States
        </li>
        <li v-if="$options.type == 'viz map allocation is-projects'">
          <span class="bubble_circle"></span>
          Project count
        </li>
        <li
          v-if="
            filters.beneficiary && $options.type == 'viz map allocation grants'
          "
        >
          <span class="square amount"></span>
          Project grants
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";

import BaseMap from "./BaseMap";

import WithCountriesMixin from "./mixins/WithCountries";
import WithFMsMixin from "./mixins/WithFMs";
import Embeddor from "./includes/Embeddor";

const AllocationMap = {
  extends: BaseMap,
  type: "allocation",

  mixins: [WithCountriesMixin, WithFMsMixin],

  components: {
    Embeddor,
    // !!! TODO: fixme. Does this work for projects? !!!
    regionDetails: {
      render() {
        return;
      },
    },
  },

  props: {
    // this is a "template" with the string 'XX' meant to be replaced
    // with the country code
    detailsDatasource: {
      type: String,
      default: true,
    },
  },

  data() {
    return {
      zoomed_nuts_level: 3,

      all_nuts_levels: [0, 3],
      // restrict rendering to donors and beneficiaries
      all_states: Object.keys(this.COUNTRIES).filter(
        (id) =>
          ["donor", "beneficiary"].indexOf(this.COUNTRIES[id].type) !== -1 &&
          id != "Intl", // let's not forget about that :)
      ),

      current_region: null,
      hovered_region: null,

      current_region_data: null,
    };
  },

  created() {
    // don't filter / aggregate by beneficiary, group by it
    // (TODO: this smells like a pattern already)
    let idx;

    idx = this.filter_by.indexOf("beneficiary");
    if (idx !== -1) this.filter_by.splice(idx, 1);

    this.aggregate_by.push({ source: "beneficiary", destination: "id" });

    idx = this.aggregate_on.findIndex((x) => x.source == "beneficiary");
    if (idx !== -1) this.aggregate_on.splice(idx, 1);

    // aggreggate on fm, we'll need that for donor colors
    this.aggregate_on.push({ source: "fm", destination: "fms", type: String });

    // cache for raw region-level data
    this._region_data = {}; // raw

    // if it's a standalone country we'll need some custom logic
    this.is_standalone = !!(this.embedded && this.filters.beneficiary);

    // these ones are used to unify beneficiary / region handling
    this.current_region = this.filters.beneficiary;
    this._prev_region = null;
  },

  computed: {
    initial_regions() {
      if (this.is_standalone)
        return [
          {
            states: this.filters.beneficiary,
            levels: [0, this.zoomed_nuts_level],
          },
        ];

      // otherwise, we always want level0 stuff, even when ready-zoomed
      const initials = [{ levels: 0 }];

      if (this.filters.beneficiary)
        initials.push({
          states: this.filters.beneficiary,
          levels: this.zoomed_nuts_level,
        });

      return initials;
    },

    data() {
      const aggregated = Object.values(this.aggregated);

      for (const item of aggregated) {
        item.name = this.BENEFICIARIES[item.id].name;
      }
      return aggregated.sort((a, b) => d3.ascending(a.name, b.name));
    },
    dropDownItems() {
      return this.data.filter((d) => !this.isHungaryException(d.id));
    },
  },

  methods: {
    getParentRegion(id) {
      if (!id) return;

      const level = this.getRegionLevel(id);
      if (level == 0) return null; // for consistency with filter values
      if (level == this.zoomed_nuts_level) return this.getAncestorRegion(id, 0);
      return this.getAncestorRegion(id, level - 1);
    },

    zoomOut() {
      this.filters.beneficiary = null;
    },

    opacityfunc(parentid) {
      return parentid == "" ? 1 : 0;
    },

    renderChart() {
      const t = this.getTransition();

      this.renderDonorColors(t);
      this.doZoom(t);
      this.renderData(t);
      this.doRenderRegionData(t); // leave this last in the chain, because...

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
      const region = this.current_region;
      if (region === null) {
        // nothing to do, but don't forget to reset the prev region
        this._prev_region = this.current_region;
        return;
      }

      const state = region.substr(0, 2);

      let dataset = this._region_data[state];

      const renderRegionData = (dataset, t) => {
        // we want to "render" the data for all ancestors of the given region.
        // (the local implementation will decide what rendering actually means)
        let r = region;
        while (r) {
          this.renderRegionData(r, this.computeRegionData(dataset), t);
          r = this.getParentRegion(r);
        }

        this._prev_region = this.current_region;
      };

      if (dataset === undefined) {
        // data might arrive too late to use the transition,
        // so prepare to reset it if necessary
        let t_expired = false;
        const t_duration = t.duration(); // so we can replicate a similar transition
        t.on("end", () => (t_expired = true));
        // TODO: run a throbber / suggest data loading somehow?

        // fetch the data, fill the cache, render
        const url = new URL(
          this.detailsDatasource.replace("XX", state),
          window.location,
        );
        url.searchParams.append("period", this.period);

        fetch(url.toString()).then((response) => {
          if (!response.ok)
            throw new Error(`${response.status} ${response.statusText}`);

          response.json().then((data) => {
            dataset = this._region_data[state] = data;
            if (t_expired) t = this.getTransition(t_duration);
            renderRegionData(dataset, t);
          });
        });
      } else {
        renderRegionData(dataset, t);
      }
    },

    computeRegionData(regiondataset) {
      const filtered = this.filter(regiondataset, this.filter_by);
      return this.aggregate(filtered, ["id"], this.aggregate_on, true);
    },

    _domouse(over, ev, d) {
      // disable mouseover events while transitioning
      if (this.transitioning) return;

      // avoid strangeness, disable events for the current region
      // (it should always be covered by its children)
      if (this.current_region && d.id == this.current_region) return;

      // disable mouseover events on mobile because of iphone quirks
      // TODO: fix this, it's too broad
      // (and events should be handled specifically for mobile as needed)
      if (window.matchMedia("(max-width: 767px)").matches) return;

      const $super = BaseMap.methods._domouse.bind(this);
      const self = $super(over, ev, d);
      if (!self) return;

      if (this.getRegionLevel(d.id) == 0 && this.isDonor(d)) return;

      return self;
    },

    clickfunc(ev, d) {
      if (d.id.length === 2 && this.COUNTRIES[d.id].type !== "beneficiary")
        return;

      const self = d3.select(ev.currentTarget);
      if (self.classed("zero")) return;

      if (d.id.length == 2) this.toggleBeneficiary(d);

      return self;
    },

    doZoom(t) {
      const newid = this.current_region,
        oldid = this._prev_region;

      if (newid == oldid) return;

      const $this = this;

      const _showchildren = (id, yes) => {
        // only select the exact region when showing,
        // otherwise hide all descendant regions
        let selector = `.regions > .${id}`;
        if (yes) {
          const level =
            id.length == 2 ? this.zoomed_nuts_level : id.length - 2 + 1;
          selector += `.level${level}`;
        }

        const parent = this.chart
          .selectAll(selector)
          //.raise()
          .classed("transitioning", true)
          .style("display", null)
          .transition(t)
          .attr("opacity", Number(yes))
          .on("end", function () {
            const s = d3.select(this).classed("transitioning", false);

            if (!yes)
              s.style("display", "none")
                // also reset regions to default color
                .selectAll("path")
                .attr("fill", $this.fillfunc);
          });
      };

      const _showregion = (id, yes) => {
        const level = this.getRegionLevel(id);

        const region = this.chart
          // must selectAll, or else data goes poof
          .selectAll(`.regions > .level${level} > .${id}`)
          .transition(t)
          .attr("fill", this.fillfunc)

          .on("start", function () {
            $this.transitioning = true;
          })
          .on("end", function () {
            $this.transitioning = false;
          })
          .on("interrupt", function (d) {
            // watch out for the impossible "double interrupt":
            // a previous country was supposed to be faded back in,
            // but that got interrupted too
            // (that's a real fast triple click in at least 2 different places)
            if (oldid && oldid != d.id && !yes) {
              $this.chart
                .select(".regions > .level0")
                .selectAll(`.${oldid}`)
                .attr("fill", $this.fillfunc);
            }
          });
      };

      if (newid) {
        // hide the selected region, show its children
        _showregion(newid, false);
        _showchildren(newid, true);
      }

      if (oldid) {
        // we need to recursively handle all ancestors of the old region,
        // until we meet the current one's parent
        let id = oldid;
        while (true) {
          // show the region, hide its children
          _showregion(id, true);
          // however, if it's an ancestor of the current one, stop
          if (newid && this.isAncestorRegion(oldid, newid)) break;
          _showchildren(id, false);

          id = this.getParentRegion(id);
          if (!id || this.isAncestorRegion(id, newid)) break;
        }
      }

      this.map.zoomTo(newid, t);
    },

    handleFilterBeneficiary(v) {
      this.current_region = v;
      if (v) this.map.renderRegions(v, this.zoomed_nuts_level);
      if (!v) this.current_region_data = null;
      this.tip.hide();
      this.render();
    },
  },
};

export default AllocationMap;
</script>

<style lang="less">
.dataviz .viz.map.allocation {
  @beneficiary: #b3dae4;
  @bubble_color: rgb(196, 17, 48);

  .chart {
    .transitioning {
      pointer-events: none;
    }

    .regions {
      @media (min-width: 768px) {
        .beneficiary:not(.zero) {
          &:hover {
            stroke: #000;
          }
        }
      }

      .level0 .beneficiary {
        @media (min-width: 768px) {
          &:not(.zero) {
            cursor: pointer;

            &:hover {
              stroke: #005494;
            }
          }
        }

        &.zero {
          cursor: not-allowed;
          //pointer-events: none;
        }
      }
    }
  }

  .toolbox {
    position: absolute;
    left: 1em;
    top: 1em;

    font-weight: bold;

    * {
      display: block;
    }

    a {
      cursor: pointer;
      padding: 0.4em;
      color: #666;
      background-color: rgba(238, 238, 238, 0.7);
      text-decoration: none;
      opacity: 0.7;

      &:hover {
        color: #3d90f3;
        background-color: #eee;
        opacity: 1;
      }
    }
  }

  .legend {
    ul {
      padding-left: 0;
    }

    li {
      list-style-type: none;
      display: inline-flex;
      align-items: center;
      margin-right: 2rem;
    }

    li:last-of-type {
      margin-right: 0;
    }

    .square {
      height: 20px;
      width: 20px;
      background: @beneficiary;
      display: inline-block;
      margin-right: 1rem;
      position: relative;
    }

    .bubble_circle {
      background: @bubble_color;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      display: inline-block;
      margin-right: 1rem;
      position: relative;
    }
  }
}
</style>
