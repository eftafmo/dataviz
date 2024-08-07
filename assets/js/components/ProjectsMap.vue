<script>
import * as d3 from "d3";

import AllocationMap from "./AllocationMap";
import ProjectsMixin from "./mixins/Projects";
import WithRegions from "./mixins/WithRegions";

const RegionDetails = {
  template: `<transition appear name="fade">
    <div class="current-region" v-if="region">
      <transition name="fade"><div :key="changed_region">
        <transition name="fade"><svg :key="changed_count"
             :width="radius * 2"
             :height="radius * 2"
             >
          <g :transform="'translate(' + radius + ',' + radius + ')'">
            <circle :r="radius" fill="#c41130" />
            <text dominant-baseline="middle" text-anchor="middle" fill="white" font-size="16" font-weight="bold">
              {{ count }}
            </text>
          </g>
        </svg></transition>
        <span>{{ label }}</span>
      </div></transition>
    </div>
  </transition>`,
  mixins: [WithRegions],
  props: {
    region: Object,
  },

  data() {
    return {
      root_label: "National-level projects",
      changed_region: 0,
      changed_count: 0,
    };
  },

  computed: {
    label() {
      return this.region.id.length === 2
        ? this.root_label
        : this.getRegionName(this.region.id) + " (" + this.region.id + ")";
    },
    count() {
      return this.getProjectCount(this.region);
    },
    radius() {
      if (!this.textDimensions) return 0;
      const len = this.count.toString().length;
      return (
        ((len === 1
          ? this.textDimensions.height
          : this.textDimensions.width * (len + 1 / 2)) /
          2) *
        1.4
      );
    },
    textDimensions() {
      return this.region && this.region.textDimensions;
    },
  },
  watch: {
    // (watching by property makes stuff get weird,
    // so this is better. region is always swapped for a new object.)
    region(a, b) {
      if (!a || !b) return;

      if (a.id !== b.id) this.changed_region = Number(!this.changed_region);

      if (this.getProjectCount(a) !== this.getProjectCount(b))
        this.changed_count = Number(!this.changed_count);
    },
  },
  methods: {
    getProjectCount(region) {
      return (
        region.project_count || (region.projects && region.projects.size) || 0
      );
    },
  },
};

export default {
  components: {
    regionDetails: RegionDetails,
  },
  extends: AllocationMap,
  mixins: [ProjectsMixin],

  data() {
    return {
      // need to set these so pointer events work in IE
      zoomed_nuts_level: 2,
      textDimensions: null,
      regionRenderOptions: null,
      all_nuts_levels: [0, 2, 3],
    };
  },
  watch: {
    isReady() {
      this.textDimensions = this.getTextDimensions();
    },
  },
  created() {
    this._rendered_bubbles = {};
  },

  mounted() {
    this.projects = this.chart.append("g").attr("class", "projects");
  },

  methods: {
    getTextDimensions() {
      // compute the dimensions of an average number character
      if (!this.isReady) return 0;

      // respect where the text will appear so css applies properly
      const fakeB = this.projects.append("g");
      const txt = fakeB
        .append("text")
        .attr("visibility", "hidden")
        .text("1234567890");

      const bounds = txt.node().getBBox();
      fakeB.remove();

      return { width: bounds.width / 10, height: bounds.height };
    },
    getradius(txt) {
      // return enough for the the text to fit, plus spacing
      // for another half a character
      const len = txt.toString().length;
      return (
        ((len === 1
          ? this.textDimensions.height
          : this.textDimensions.width * (len + 1 / 2)) /
          2) *
        1.3
      ); // divided by 2 because radius, and multiplied
      // because a lil' bit of hardcoded extra
    },

    zoomOut() {
      const current = this.filters.region;

      if (!current) {
        // no region selected, unset the country
        this.filters.beneficiary = null;
      } else {
        // reset to country level
        this.filters.region = null;
      }
    },

    tooltipTemplate(ev, d) {
      if (this.isHungaryException(d.id)) return this.hungaryTooltipTemplate();
      const level = this.getRegionLevel(d.id);
      const allocation = d.allocation || 0,
        num_projects = this.getprojectcount(d),
        country_is_donor =
          d.id.length === 2 && this.COUNTRIES[d.id].type === "donor",
        state_type = country_is_donor ? "donor-tooltip" : "";

      let details = `
        <li>
          ${this.number(num_projects)} 
          ${this.singularize("projects", num_projects)} 
        </li>
      `;

      if (d.programmes) {
        details = `
        <li>
          ${this.number(num_projects)}
          ${this.singularize("projects", num_projects)}
        </li>
        <li>${this.currency(allocation)} gross allocation</li>
        <li>
          ${d.sectors.size}
          ${this.singularize("sectors", d.sectors.size)}
        </li>
        <li>
          ${d.areas.size}
          ${this.singularize("programme areas", d.areas.size)}
        </li>
        <li>
          ${d.programmes.size}
          ${this.singularize("programmes", d.programmes.size)}
        </li>
      `;
      }

      if (level === 0) {
        const country_details = country_is_donor
          ? ""
          : `
                <ul>
                  ${details}
                </ul>
                <span class="action">Click to filter by Beneficiary State</span>
              `;

        return (
          `
          <div class="title-container ${state_type}">
            <img src="${this.get_flag(d.id)}" alt="" />
            <span class="name">${this.COUNTRIES[d.id].name}</span>
          </div>` + country_details
        );
      } else {
        const action =
            level === 3
              ? "Click to filter news by region"
              : `Click to display NUTS${level} regions`,
          country_details = country_is_donor
            ? ""
            : `
                <ul>
                  ${details}
                </ul>
                <span class="action">${action}</span>
              `;

        return (
          `
          <div class="title-container ${state_type}">
            <img src="${this.get_flag(d.id)}" alt="" />
            <span class="name">${this.getRegionName(d.id)} (${d.id})</span>
          </div>` + country_details
        );
      }
    },
    getprojectcount(d) {
      return d.project_count || (d.projects && d.projects.size) || 0;
    },
    _domouse(over, ev, d) {
      const $super = AllocationMap.methods._domouse.bind(this);
      const self = $super(over, ev, d);
      if (!self) return;

      // (de)highlight the bubble
      const id = d.id,
        level = id.length - 2;

      const _selector = level != 0 ? "." + id.substr(0, 2) : "",
        selector = `${_selector}.level${level} > g.region.${id}`;

      const bubble = this.projects.select(selector);

      bubble.classed("hovered", over);

      if (over) bubble.raise();

      // TODO: this shouldn't be handled here, but in AllocationMap or BaseMap
      self
        .transition(this.getTransition(this.short_duration))
        .attr("fill", over ? this.hovered_region_color : this.fillfunc);
    },

    clickfunc(ev, d) {
      const $super = AllocationMap.methods.clickfunc.bind(this);
      const self = $super(ev, d);
      if (!self) return;

      if (d.id.length != 2) this.filters.region = d.id;

      this.chart
        .select(".regions")
        .selectAll(".selected")
        .classed("selected", false);

      if (d.id.length > 4) {
        d3.select(ev.currentTarget).classed("selected", true);
      }
    },

    _getChildrenLevel(region) {
      if (!region) return 0;

      const lvl = region.length - 2;
      return lvl < this.zoomed_nuts_level ? this.zoomed_nuts_level : lvl + 1;
    },

    _getRegionSelector(region) {
      const level = this._getChildrenLevel(region);
      const _selector = region ? "." + region : "";

      return `g${_selector}.level${level}`;
    },

    getBubbles(parentid) {
      const main = !parentid;

      const level = this._getChildrenLevel(parentid),
        selector = this._getRegionSelector(parentid);

      if (this._rendered_bubbles[parentid])
        return this.projects.select(selector);

      // else do the initial render of all the bubbles
      const regions = this.chart
        .selectAll(`.regions > ${selector} > path.beneficiary`)
        .data();

      const _classes = [`level${level}`];
      // add all parent regions as class names
      let r = parentid;
      while (r) {
        _classes.push(r);
        r = this.getParentRegion(r);
      }

      const parent = this.projects
        .append("g")
        .attr("opacity", 0)
        .attr("class", _classes.join(" "));

      const _c = (d) => this.map.geodetails[d.id].centroid;

      const containers = parent
        .selectAll("g")
        .data(regions)
        .enter()
        .append("g")
        .attr("class", (d) => `region ${d.id}`)
        //.attr("opacity", 0)
        .property("_value", 0);

      if (!main) {
        const k = 1 / this.map.geodetails[parentid].transform.k;

        containers.attr(
          "transform",
          (d) =>
            `translate(${_c(d).x * (1 - k)},${_c(d).y * (1 - k)}) scale(${k})`,
        );
      }

      containers
        .append("circle")
        .attr("cx", (d) => _c(d).x)
        .attr("cy", (d) => _c(d).y)
        .attr("fill", "rgb(196, 17, 48)")
        .attr("fill-opacity", 0.4)
        .attr("transform-origin", "50% 50%");

      containers
        .append("text")
        .attr("x", (d) => _c(d).x)
        .attr("y", (d) => _c(d).y)
        .attr("font-size", "1.2em")
        .attr("text-anchor", "middle")
        .attr("fill", "#fff")
        .attr("font-weight", "bold")
        .attr("dy", ".33em"); // magical self-centering offset

      this._rendered_bubbles[parentid] = true;
      return parent;
    },

    updateProjects(regions, t) {
      const $this = this;

      // it's easier to use a fake transition
      // (than mess with transition vs raw context below)
      if (t === undefined) t = this.getTransition(0);

      // since the bubbles always exist, we must simulate enter vs update
      const rupdate = regions.filter(function (d) {
        const oldv = this._value;
        return oldv != 0 && $this.getprojectcount(d) != oldv;
      });

      const rentered = regions.filter(function (d) {
        const oldv = this._value;
        return oldv == 0 && $this.getprojectcount(d) != 0;
      });

      const rexit = regions.exit().merge(
        regions.filter(function (d) {
          const oldv = this._value;
          return oldv != 0 && $this.getprojectcount(d) == 0;
        }),
      );

      // update gets the circle dimension transitioned
      rupdate
        .select("circle")
        .transition(t)
        .attr("r", (d) => this.getradius(this.getprojectcount(d)));

      // and the text swapped in
      rupdate
        .select("text")
        .each(function () {
          // clone the old text and fade it out
          const clone = d3.select(
            this.parentNode.appendChild(this.cloneNode(true)),
          );
          clone
            .attr("opacity", 1)
            .transition(t)
            .attr("opacity", 0)
            .on("end", function () {
              clone.remove();
            });
        })
        // while the real thing gets faded in
        .attr("opacity", 0)
        .text(this.getprojectcount)
        .transition(t)
        .attr("opacity", 1);

      // enter gets faded in
      rentered
        .select("circle")
        .attr("r", (d) => this.getradius(this.getprojectcount(d)));

      rentered.select("text").text(this.getprojectcount);

      rentered.transition(t).attr("opacity", 1);

      // exit gets faded out
      rexit
        .transition(t)
        .attr("opacity", 0)
        // also clear everything just to be nice
        .on("end", function () {
          const self = d3.select(this);
          self.select("circle").attr("r", null);
          self.select("text").text("");
        });

      // finally,
      regions.property("_value", this.getprojectcount);
      regions.exit().property("_value", 0);
    },

    _renderRegionData(parentid, dataset, t) {
      if (t === undefined) t = this.getTransition();

      const parent = this.getBubbles(parentid);

      const regions = parent.selectAll("g.region").data(dataset, (d) => d.id);

      // bind the data to the map as well, because that's where
      // the mouse events happen
      const mapregions = this.chart
        .selectAll(
          `.regions > ${this._getRegionSelector(parentid)} > path.beneficiary`,
        )
        .data(dataset, (d) => d.id);

      mapregions
        .classed("zero", false)
        .transition(t)
        .attr("fill", this.fillfunc);

      // reset the 0ed ones
      mapregions
        .exit()
        .classed("zero", true)
        .each(function () {
          const self = d3.select(this),
            id = self.datum().id;

          self.datum({
            id: id,
          });
        })
        .transition(t)
        .attr("fill", (d) =>
          this.getRegionLevel(d.id) == 0
            ? this.beneficiary_color_zero
            : this.region_color_zero,
        );

      // we only go this far if this isn't the current region
      // (we just want to bind data for the tooltip to work)
      if (parentid !== this.current_region) return;

      const changed = this._prev_region != parentid;

      if (!changed) {
        // if the region is unchanged then bubble content gets transitioned
        regions.call(this.updateProjects, t);
        // also make sure the bubbles are visible, because initial render
        parent.attr("opacity", 1);
        // and that's it
        return;
      }

      // otherwise, no transition here
      regions.call(this.updateProjects);

      // but fade in the main container
      parent.style("display", null).transition(t).attr("opacity", 1);

      // and out the old
      this.getBubbles(this._prev_region)
        .classed("transitioning", true)
        .transition(t)
        .attr("opacity", 0)
        .on("end", function () {
          d3.select(this)
            .style("display", "none")
            .classed("transitioning", false);
        });

      // also "un-hover" bubbles because they sometimes get stuck
      this.projects.selectAll("g.hovered").classed("hovered", false);
    },

    renderData(t) {
      const dataset = Object.values(this.data);
      this._renderRegionData(null, dataset, t);
    },

    renderRegionData(region, regiondata, t) {
      const aggregated = this._mkLevelData(region, regiondata);
      const dataset = Object.values(aggregated);

      this._renderRegionData(region, dataset, t);

      // keep the current region data around, it's used for "the parent bubble"
      if (region == this.current_region) {
        if (aggregated[region]) {
          this.current_region_data = {
            ...aggregated[region],
            textDimensions: this.textDimensions,
          };
        } else {
          this.current_region_data = {
            id: this.current_region,
            textDimensions: this.textDimensions,
          };
        }
      }
    },

    _mkLevelData(parentid, data) {
      // re-aggregate the data to compute per-level stuff
      const out = {};

      const _aggregate = (id, row) => {
        let item = out[id];
        if (item === undefined) {
          item = out[id] = {};

          for (const k in row) {
            // can't simply Object.assign, because of sets
            const v = row[k];

            if (v instanceof Set) item[k] = new Set(v.values());
            else item[k] = v;

            // overwrite id
            item.id = id;
          }
        } else {
          for (const k in row) {
            const v = row[k];

            if (typeof v == "string") continue;
            else if (typeof v == "number") item[k] += v;
            else if (v instanceof Set) v.forEach((x) => item[k].add(x));
            else console.error("Unhandled key / value", k, v);
          }
        }
      };

      const plvl = this.getRegionLevel(parentid);

      for (const row of data) {
        if (!this.isAncestorRegion(parentid, row.id)) continue;

        const rlvl = this.getRegionLevel(row.id);
        let agglvl;

        // regions below zoomed_nuts_level, as well as regions of the form
        // '??Z*' (that is, "extra-regio") get counted towards the country
        if (rlvl < this.zoomed_nuts_level || row.id.substr(2, 1) == "Z") {
          agglvl = 0;
        } else {
          // aggregate under parent's first-ish level descendants
          agglvl =
            plvl < this.zoomed_nuts_level ? this.zoomed_nuts_level : plvl + 1;
        }

        const aggid = this.getAncestorRegion(row.id, agglvl);
        _aggregate(aggid, row);
      }

      return out;
    },

    handleFilterBeneficiary(newid, oldid) {
      this.$super().handleFilterBeneficiary(newid, oldid);
      // unset the region filter
      this.filters.region = null;
    },

    handleFilterRegion(v, old) {
      // has this been triggered by a change in beneficiary?
      const beneficiary = this.filters.beneficiary;
      if (!v && old && (!beneficiary || old.substr(0, 2) != beneficiary))
        return;

      const level = v && this.getRegionLevel(v);

      // at level 3 there's nothing to do
      if (level == 3) return;

      // otherwise
      this.tip.hide();
      if (v) this.map.renderRegions(v, level + 1);

      this.current_region = v ? v : beneficiary;
      this.render();
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.map.is-projects {
  @bubble_color: rgb(196, 17, 48);
  @nuts3_selected_color: rgb(3, 152, 251);

  .bubble {
    text {
      user-select: none;
    }
  }

  .chart {
    .regions .beneficiary {
      cursor: pointer;

      &.zero {
        cursor: not-allowed;
      }
    }

    .projects > g > g {
      pointer-events: none;

      .bubble;

      &.hovered circle {
        fill-opacity: 1;
      }
    }
  }

  .current-region {
    position: absolute;
    left: 4.2em;
    top: 0.7em;

    width: ~"calc(100% - 4em)";

    div {
      position: absolute;
      top: 0;
      padding: 0.5em 0.7em 0.5em 1.5em;
      background-color: rgba(238, 238, 238, 0.2);
      color: black;
      border: 1px solid rgba(0, 0, 0, 0.2);
      border-radius: 2px;

      svg {
        position: absolute;
        left: 0;
        top: 50%;
        transform: translate(-50%, -50%);
        box-shadow: none;

        .bubble;
      }
    }
  }

  .selected {
    fill: @nuts3_selected_color;
    fill-opacity: 0.5;
    transition: fill 0.4s ease;
  }
}
</style>
