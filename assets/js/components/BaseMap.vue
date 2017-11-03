<!--
  // ATTENTION: map-base must be used like this:

  <map-base
      ref="map"
      v-on:rendered="handleMapRendered"
  >
-->

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


<script>
import * as d3 from 'd3'
import {fmcolour} from './mixins/WithFMs'

import Chart from './Chart'
import MapBase from './includes/MapBase'

import WithRegionsMixin from './mixins/WithRegions'
import WithTooltipMixin from './mixins/WithTooltip'


// jumping through hoops because of vue's lack of template inheritance.
// don't forget to add this to the template.
const PijamaDefs = {
  template: `<svg class="defs">
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
  </svg>`,

  methods: {
    fmcolour,
  },
}

export default Chart.extend({
  type: "map",

  mixins: [
    WithRegionsMixin,
    WithTooltipMixin,
  ],

  components: {
    "map-base": MapBase,
    "pijama-defs": PijamaDefs,
  },

  data() {
    let origin = "";
    if (this.datasource) {
      const host = this.datasource.replace(/^(https?:)?\/\/([^\/]+)\/.*$/, '$2')
      origin = location.protocol +'//' + host;
    }

    return {
      origin: origin,

      beneficiary_colour: 'rgba(221, 221, 221, 1)',
      beneficiary_colour_zero: 'rgba(238, 238, 238, 1)',
      region_colour: 'rgba(221, 221, 221, 0.5)',
      region_colour_zero: 'rgba(238, 238, 238, 0.5)',

      hovered_region_colour: 'rgba(150, 210, 249, 0.5)',
      current_region_colour: 'rgba(221, 238, 255, 1)',
      ancestor_region_colour: 'rgba(221, 238, 255, 0)',

      donor_colour_inactive: "#fff",

      width: 0,
      height: 0,

      map_rendered: false,
    };
  },

  mounted() {
    const map = this.map = this.$refs.map;
    this.width = map.width;
    this.height = map.height;
  },

  computed: {
    rendered() {
      return this.map_rendered && this.chart_rendered;
    },

    isReady() {
      return !!(this.hasData
               && this.is_mounted
               && this.map_rendered)
    },
  },

  methods: {
    handleMapRendered() {
      this.map_rendered = true
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

    registerEvents(selection) {
      selection
        .on("click", this.clickfunc)
        .on("mouseenter", this.mouseenterfunc)
        .on("mouseleave", this.mouseleavefunc)
    },

    clickfunc(d, i, group) {
      return
    },

    mouseenterfunc(d, i, group) {
      return this._domouse(true, d, i, group)
    },

    mouseleavefunc(d, i, group) {
      return this._domouse(false, d, i, group)
    },

    _domouse(over, d, i, group) {
      const thisnode = group[i]
      const self = d3.select(thisnode)

      // disable mouse-over when zeroed
      if (self.classed("zero")) return

      if (over) {
        self.raise()
        // we would normally want to raise the parent container too,
        // but we won't, because the current parent region is always
        // visible (currently) and it would cover its children
        //d3.select(thisnode.parentNode).raise()

        this.tip.show.call(self.node(), d, i)
        this.hovered_region = d
      } else {
        this.tip.hide.call(self.node(), d, i)
        this.hovered_region = null
      }

      return self
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
        // the dataset is the source of truth.
        // normally we already looped over if and have it aggregated:
        if (this.data instanceof Array) {
          for (const row of this.data) {
            if (!with_eea && row.fms.has(eea))
              with_eea = true

            if (!with_no && row.fms.has(no))
              with_no = true

            if (with_eea && with_no) break
          }
        } else {
          // we need to loop over the entire filtered dataset
          for (const row of this.filtered) {
            if (!with_eea && row.fm == eea)
              with_eea = true

            if (!with_no && row.fm == no)
              with_no = true

            if (with_eea && with_no) break
          }
        }
      }

      // TODO: FIXME. this dreadful thing is necessary for now
      // because of partners' custom aggregation
      if (!with_eea && !with_no) {
        with_eea = with_no = true
      }

      // EEA donors are either coloured or inactive
      this.chart.select(".regions").selectAll("path.donor")
        .filter(d => this.getAncestorRegion(d.id, 0) != "NO")
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

      d3.select("pattern#multi-fm").selectAll("rect")
        .datum(function() { return this.getAttribute("class") })
        .transition(t)
        .attr("fill", colourfuncNO)
        .attr("stroke", colourfuncNO)
    },

    fillfunc(d, i, group) {
      // returns the fill colour of a country or region
      const id = d.id,
            level = this.getRegionLevel(id),
            country = this.getAncestorRegion(id, 0),
            type = this.COUNTRIES[country].type;

      if (type == "donor") {
        if (country == "NO")
          return "url(#multi-fm)"

        if (this.filters.fm == "Norway Grants")
          return this.donor_colour_inactive

        return this.fmcolour("eea-grants")
      }

      if (this.current_region) {
        if (id == this.current_region)
          return this.current_region_colour

        if (this.isAncestorRegion(id, this.current_region))
          return this.ancestor_region_colour
      }

      if (level == 0)
        return this.beneficiary_colour

      return this.region_colour
    },
  },
})
</script>
