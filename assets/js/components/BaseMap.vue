<!--
  // ATTENTION: map-base must be used like this:

  <map-base
      ref="map"
      v-on:rendered="handleMapRendered"
  >
-->

<script>
import * as d3 from "d3";
import d3tip from "d3-tip";
import WithFMs from "./mixins/WithFMs";

import Chart from "./Chart";
import MapBase from "./includes/MapBase";

import WithRegionsMixin from "./mixins/WithRegions";
import WithTooltipMixin from "./mixins/WithTooltip";

// jumping through hoops because of vue's lack of template inheritance.
// don't forget to add this to the template.
const PijamaDefs = {
  mixins: [WithFMs],
  template: `<svg class="defs">
    <defs>
      <pattern id="multi-fm" width="50" height="11" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="50" height="6"
              class="norway-grants"
              :fill="fmcolor('norway-grants')"
              :stroke="fmcolor('norway-grants')"
        />
        <rect x="0" y="6" width="50" height="5"
              class="eea-grants"
              :fill="fmcolor('eea-grants')"
              :stroke="fmcolor('eea-grants')"
        />
      </pattern>
    </defs>
  </svg>`,
};

export default {
  components: {
    "map-base": MapBase,
    "pijama-defs": PijamaDefs,
  },
  extends: Chart,
  type: "map",

  mixins: [WithRegionsMixin, WithTooltipMixin],

  data() {
    if (this.datasource) {
      const host = this.datasource.replace(
        /^(https?:)?\/\/([^\/]+)\/.*$/,
        "$2"
      );
    }

    return {
      beneficiary_color: "#b3dae4",
      beneficiary_color_zero: "#c2cdd3",
      region_color: "rgba(221, 221, 221, 0.5)",
      region_color_zero: "rgba(238, 238, 238, 0.9)",

      hovered_region_color: "rgba(150, 210, 249, 0.5)",
      current_region_color: "rgba(221, 238, 255, 1)",
      ancestor_region_color: "rgba(221, 238, 255, 0)",

      donor_color_inactive: "#fff",

      width: 0,
      height: 0,

      map_rendered: false,
    };
  },

  computed: {
    rendered() {
      return this.map_rendered && this.chart_rendered;
    },

    isReady() {
      return !!(this.hasData && this.is_mounted && this.map_rendered);
    },
  },

  mounted() {
    const map = (this.map = this.$refs.map);
    this.width = map.width;
    this.height = map.height;
  },

  methods: {
    handleMapRendered() {
      this.map_rendered = true;
    },

    tooltipTemplate() {
      throw new Error("Not implemented");
    },

    createTooltip() {
      let tip = d3tip()
        .attr("class", "dataviz-tooltip map")
        .html(this.tooltipTemplate)
        .direction("n")
        .offset([0, 0]);

      this.tip = tip;
      this.chart.call(this.tip);
    },

    registerEvents(selection) {
      selection
        .on("click", this.clickfunc)
        .on("mouseenter", this.mouseenterfunc)
        .on("mouseleave", this.mouseleavefunc);
    },

    clickfunc(ev, d) {},

    mouseenterfunc(ev, d) {
      return this._domouse(true, ev, d);
    },

    mouseleavefunc(ev, d) {
      return this._domouse(false, ev, d);
    },

    _domouse(over, ev, d) {
      const thisnode = ev.currentTarget;
      const self = d3.select(thisnode);

      // disable mouse-over when zeroed
      // if (self.classed("zero")) return;

      if (over) {
        self.raise();
        // we would normally want to raise the parent container too,
        // but we won't, because the current parent region is always
        // visible (currently) and it would cover its children
        //d3.select(thisnode.parentNode).raise()

        this.tip.show.call(ev.currentTarget, ev, d);
        this.hovered_region = d;
      } else {
        this.tip.hide.call(ev.currentTarget, ev, d);
        this.hovered_region = null;
      }

      return self;
    },

    renderDonorColors(t) {
      let with_eea = false,
        with_no = false;

      const eea = this.FMS["eea-grants"].name,
        no = this.FMS["norway-grants"].name;

      const fmfilter = this.filters.fm;

      if (fmfilter == eea) with_eea = true;
      else if (fmfilter == no) with_no = true;
      else {
        // the dataset is the source of truth.
        // normally we already looped over if and have it aggregated:
        if (this.data instanceof Array) {
          for (const row of this.data) {
            if (!with_eea && row.fms.has(eea)) with_eea = true;

            if (!with_no && row.fms.has(no)) with_no = true;

            if (with_eea && with_no) break;
          }
        } else {
          // we need to loop over the entire filtered dataset
          for (const row of this.filtered) {
            if (!with_eea && row.fm == eea) with_eea = true;

            if (!with_no && row.fm == no) with_no = true;

            if (with_eea && with_no) break;
          }
        }
      }

      // TODO: FIXME. this dreadful thing is necessary for now
      // because of partners' custom aggregation
      if (!with_eea && !with_no) {
        with_eea = with_no = true;
      }

      // EEA donors are either colored or inactive
      this.chart
        .select(".regions")
        .selectAll("path.donor")
        .filter((d) => this.getAncestorRegion(d.id, 0) != "NO")
        .transition(t)
        .attr(
          "fill",
          with_eea ? this.fmcolor("eea-grants") : this.donor_color_inactive
        );

      // Norway donors are handled via the pattern fill
      const colorfuncNO = (id) => {
        if (with_eea && with_no) return this.fmcolor(id);

        if (with_eea) return this.fmcolor("eea-grants");
        if (with_no) return this.fmcolor("norway-grants");
      };

      d3.select("pattern#multi-fm")
        .selectAll("rect")
        .datum(function () {
          return this.getAttribute("class");
        })
        .transition(t)
        .attr("fill", colorfuncNO)
        .attr("stroke", colorfuncNO);
    },

    fillfunc(d, i, group) {
      // returns the fill color of a country or region
      const id = d.id || d.properties.id,
        level = this.getRegionLevel(id),
        country = this.getAncestorRegion(id, 0),
        type = this.COUNTRIES[country].type;

      if (type == "donor") {
        if (country == "NO") return "url(#multi-fm)";

        if (this.filters.fm == "Norway Grants")
          return this.donor_color_inactive;

        return this.fmcolor("eea-grants");
      }

      if (this.current_region) {
        if (id == this.current_region) return this.current_region_color;

        if (this.isAncestorRegion(id, this.current_region))
          return this.ancestor_region_color;
      }

      if (level == 0) return this.beneficiary_color;

      return this.region_color;
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.map {
  svg.defs {
    height: 0;
    width: 0;
    position: fixed;
    top: 0;
    left: 0;
    opacity: 0;
  }
}
</style>

