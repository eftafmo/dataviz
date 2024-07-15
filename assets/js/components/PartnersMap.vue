<template>
  <div :class="classNames">
    <slot v-if="!embedded" name="title"></slot>

    <div class="selector">
      Show:
      <label>
        <input
          id="programmes"
          v-model="visible_layers"
          type="checkbox"
          value="programmes"
        />
        <label for="programmes"></label>
        Donor Programme Partners
      </label>
      <label>
        <input
          id="projects"
          v-model="visible_layers"
          type="checkbox"
          value="projects"
        />
        <label for="projects"></label>
        Donor project partners
      </label>
    </div>

    <map-base
      ref="map"
      :period="period"
      :all-levels="[3]"
      :fillfunc="fillfunc"
      :zoomable="false"
      @rendered="handleMapRendered"
      @regions-rendered="registerEvents"
    >
      <pijama-defs ref="defs"></pijama-defs>
      <g class="partnerships">
        <g v-for="layer in layers" :key="layer" :class="layer" class="base"></g>
      </g>
    </map-base>
  </div>
</template>

<script>
import * as d3 from "d3";
import { slugify } from "@js/lib/util";

import BaseMap from "./BaseMap";

import PartnersMixin from "./mixins/Partners";
import WithFMsMixin from "./mixins/WithFMs";
import WithCountriesMixin from "./mixins/WithCountries";

export default {
  extends: BaseMap,
  mixins: [PartnersMixin, WithFMsMixin, WithCountriesMixin],

  props: {
    layers: {
      type: Array,
      // note the order. (makes sure "programmes" is always on top in svgs)
      default: () => ["projects", "programmes"],
    },
  },

  data() {
    return {
      visible_layers: this.layers,
      region: null,

      region_color: "#ccc",

      chart_opacity: 1.0,
      region_opacity: 0.8,

      default_opacity: 0.8,
      highlighted_opacity: 0.9,
      faded_opacity: 0.2,
    };
  },

  computed: {
    current_layers() {
      // like visible_layers, but preserving order
      return this.layers.filter((x) => this.visible_layers.indexOf(x) !== -1);
    },

    scale() {
      return this.chartWidth / this.width;
    },

    aggregated() {
      /*
        this exists because we need to compute two datasets:

        - the region-to-region array, for drawing the connections.
          must be grouped by type (programme / project) and source country;

        - the array of regions involved, for showing on the map, resembling
          what we would "normally" aggregate.
          must contain aggregated FMs (so the donor colors can be derived).
      */

      const dataset = this.filtered;

      const connections = {
          programmes: {},
          projects: {},
        },
        // group regions by type as well, so we can use the type
        // as a "data filter" later on
        regions = {
          programmes: {},
          projects: {},
        };

      const _getConnectionGroup = (type, id) => {
        // grouping by country
        const country = this.getAncestorRegion(id, 0);

        let group = connections[type][country];
        if (group === undefined) group = connections[type][country] = {};

        return group;
      };

      const _getRegion = (type, id) => {
        let region = regions[type][id];
        if (region === undefined)
          region = regions[type][id] = {
            //id: id, // skipping this because data() reaggregates anyway
            fms: new Set(),
            states: new Set(),
            bs_orgs: new Set(),
            ds_orgs: new Set(),
            programmes: new Set(),
            projects: new Set(),
            // add here anything else you might want to aggregate on
          };
        return region;
      };

      const _setData = (type, source, target, ds_orgs, bs_orgs, d) => {
        const conngroup = _getConnectionGroup(type, source);
        conngroup[`${source}-${target}`] = { source, target };
        const projects = new Set();
        for (const prj in d.projects) {
          if (
            d.projects[prj]["src_nuts"].indexOf(source) !== -1 &&
            d.projects[prj]["dst_nuts"].indexOf(target) !== -1
          ) {
            projects.add(prj);
          }
        }
        if (source) {
          const region = _getRegion(type, source);
          region.fms.add(d.fm);
          ds_orgs.forEach((x) => region.ds_orgs.add(x));
          bs_orgs.forEach((x) => region.bs_orgs.add(x));
          region.programmes.add(d.programme);
          projects.forEach((x) => region.projects.add(x));
          if (target) region.states.add(target.substr(0, 2));
        }
        if (target) {
          const region = _getRegion(type, target);
          region.fms.add(d.fm);
          ds_orgs.forEach((x) => region.ds_orgs.add(x));
          bs_orgs.forEach((x) => region.bs_orgs.add(x));
          region.programmes.add(d.programme);
          projects.forEach((x) => region.projects.add(x));
          if (source) region.states.add(source.substr(0, 2));
        }
      };

      for (const d of dataset) {
        let type;

        type = "programmes";
        for (const po_code in d.PO) {
          if (!d.DPP_nuts) continue;
          // we can have rows with PO but not DPP (only projects)
          const source = d.DPP_nuts,
            target = d.PO[po_code].nuts,
            ds_orgs = new Set().add(d.DPP),
            bs_orgs = new Set().add(po_code);

          _setData(type, source, target, ds_orgs, bs_orgs, d);
        }

        type = "projects";
        for (const prj_nuts of d.prj_nuts) {
          if (!prj_nuts.dst) continue;
          // many project partners don't have nuts. let them be
          // we do want to see donor project partners with no nuts, though
          const source = prj_nuts.src,
            target = prj_nuts.dst;
          const ds_orgs = new Set();
          for (const org in d.PJDPP) {
            if (d.PJDPP[org].nuts === source) ds_orgs.add(org);
          }
          const bs_orgs = new Set();
          for (const org in d.PJPT) {
            if (d.PJPT[org].nuts === target) bs_orgs.add(org);
          }

          _setData(type, source, target, ds_orgs, bs_orgs, d);
        }
      }

      // flatten the connections data
      for (const type in connections) {
        const collection = [];
        for (const country in connections[type]) {
          collection.push({
            country: country,
            connections: Object.values(connections[type][country]),
          });
        }
        connections[type] = collection;
      }

      return { regions, connections };
    },

    data() {
      const datasets = this.aggregated.regions;
      // merge the regions together
      // NOTE: if we want to filter by type this is where we can do it
      const out = {};

      for (const type in datasets) {
        const dataset = datasets[type];

        for (const id in dataset) {
          let region = out[id];
          if (region === undefined)
            region = out[id] = {
              id: id,
              fms: new Set(),
            };
          if (region[type] === undefined) {
            region[type] = {
              states: new Set(),
              ds_orgs: new Set(),
              bs_orgs: new Set(),
              programmes: new Set(),
              projects: new Set(),
            };
          }

          dataset[id].fms.forEach((x) => region.fms.add(x));
          dataset[id].states.forEach((x) => region[type].states.add(x));
          dataset[id].ds_orgs.forEach((x) => region[type].ds_orgs.add(x));
          dataset[id].bs_orgs.forEach((x) => region[type].bs_orgs.add(x));
          dataset[id].programmes.forEach((x) => region[type].programmes.add(x));
          dataset[id].projects.forEach((x) => region[type].projects.add(x));
        }
      }

      return Object.values(out);
    },
  },

  watch: {
    visible_layers: "handleLayers",
  },

  mounted() {
    // make remote territories visible
    // this is very ugly. TODO: fix... somehow.. better
    this.chart.attr("transform", "translate(60,0)");
  },

  methods: {
    tooltipTemplate(ev, d) {
      const dId = d.id || d.properties.id;
      const country = this.getAncestorRegion(dId, 0);

      const is_ds = this.COUNTRIES[country].type !== "beneficiary";
      let details = "";
      let _plm = (prefix, word, count) =>
        `${count} ${prefix} ${this.pluralize(word, count)}`;
      let _line = (src_text, dst_text, in_text, is_ds) => {
        if (is_ds) [src_text, dst_text] = [dst_text, src_text];
        return `<li>${src_text} working with ${dst_text} in ${in_text}</li>`;
      };
      if (d.programmes) {
        details += _line(
          _plm("programme", "operator", d.programmes.bs_orgs.size),
          _plm("Donor", "partner", d.programmes.ds_orgs.size),
          _plm("", "programme", d.programmes.programmes.size),
          is_ds,
        );
      }
      if (d.projects) {
        details += _line(
          _plm("project", "promoter", d.projects.bs_orgs.size),
          _plm("Donor", "partner", d.projects.ds_orgs.size),
          _plm("", "project", d.projects.projects.size),
          is_ds,
        );
      }

      return `
        <div class="title-container">
          <img src="${this.get_flag(country)}" alt="" />
          <span class="name">${this.getRegionName(dId)} (${dId})</span>
        </div>
        <ul>
          ${details}
        </ul>`;
    },

    renderChart() {
      const t = this.getTransition();

      this.renderDonorColors(t);
      this.renderRegionData(t);
      this.renderConnections(t);
      this.renderVisibleLayers(t);

      d3.selectAll(".chart .regions").attr("stroke-opacity", 0.5);
      d3.selectAll(".chart .regions path.zero")
        .attr("fill", "none")
        .attr("stroke", "none");
      d3.selectAll(".dataviz .viz.map .partnerships")
        .attr("stroke-width", 1.5)
        .attr("fill", "none");
    },

    renderRegionData(t) {
      // "render". this only updates the data so the tooltip works.
      // TODO: transition the zero <-> non-zero beneficiaries
      const regions = this.chart
        .selectAll(".regions > g > path")
        .data(this.data, (d) => d.id || d.properties.id);

      regions.classed("zero", false);

      regions.exit().classed("zero", true);
    },

    renderConnections(t) {
      // don't transition connections in IE. not nice, but necessary.
      const is_ie = !!document.documentMode;
      if (is_ie) t = this.getTransition(0);

      // we render from the donor side
      const conndata = this.aggregated.connections;

      for (const type in conndata) {
        this._renderConnections(type, Object.values(conndata[type]), t);
      }
    },

    _renderConnections(type, data, t) {
      const container = this.chart.select(`.partnerships > .base.${type}`),
        regions = container.selectAll("g").data(data, (d) => d.country);

      const getColor = (d) => {
        const color = this.colors[type];

        if (!this.filters.fm) return color;

        const country = d.country,
          fms = this.COUNTRIES[country].fms;

        if (!fms || fms.indexOf(slugify(this.filters.fm)) === -1)
          return this.weak_colors[type];
        else return color;
      };

      // connections are grouped by source state. will help us transition
      // to grayscale when filtering by fm
      const rentered = regions
        .enter()
        .append("g")
        .attr("class", (d) => d.country)
        .attr("stroke", getColor);

      regions.transition(t).attr("stroke", getColor);

      const rexit = regions.exit().remove();

      const connections = regions
        .merge(rentered)
        .selectAll("path")
        .data(
          (d) => d.connections,
          (d) => d.source + "-" + d.target,
        );

      const _badids = new Set();

      const getArc = (source, target) => {
        // TODO: memoize this
        // the simple approach would be to draw an arc with the same radius
        // as the distance between points, but we're gonna use a quadratic
        // curve instead, which allows us to mess with the arc's radius
        // programmatically §
        // (also, we can use the same calculations to draw into a canvas)

        const o0 = this.map.geodetails[source];
        const o1 = this.map.geodetails[target];

        if (o0 === undefined) _badids.add(source);
        if (o1 === undefined) _badids.add(target);
        if (o0 === undefined || o1 === undefined) return;

        const k = 1; // this.scale if drawing into a canvas

        const p0 = o0.centroid,
          p1 = o1.centroid,
          x0 = p0.x * k,
          y0 = p0.y * k,
          x1 = p1.x * k,
          y1 = p1.y * k,
          // distance between points
          _dx = x1 - x0,
          _dy = y1 - y0,
          // radius
          r = Math.sqrt(_dx * _dx + _dy * _dy),
          // sign
          s = x1 >= x0 ? 1 : -1,
          // midpoint
          _mx = (x0 + x1) / 2,
          _my = (y0 + y1) / 2,
          // distance from midpoint (perpendicular)
          _d = r * (1 - Math.sqrt(3) / 2) * 2,
          // actual offsets from midpont
          _ox = _dy * (_d / r),
          _oy = _dx * (_d / r);

        // the control point
        let x = _mx + s * _ox,
          y = _my - s * _oy;

        // a little hack for iceland - portugal links §
        if (x < 0) {
          x = _mx + (s * _ox) / 2;
          y = _my - (s * _oy) / 2;
        }

        //return `M ${ x0 },${ y0 } A ${ r },${ r } 0 0,${ (s + 1) / 2 } ${ x1 },${ y1 }`
        return `M ${x0},${y0} Q ${x},${y} ${x1},${y1}`;

        // ctx.quadraticCurveTo(x, y, x1, y1);
      };

      // because performing transitions on hundreds of paths kills rendering,
      // connections that enter / exit will instead be moved to a different
      // layer, and transitioned all at once

      const connentered = connections
        .enter()
        .append("path")
        .attr("class", (d) => `${d.source} ${d.target}`)
        .attr("d", (d) => getArc(d.source, d.target));

      // (some error checking)
      if (_badids.size !== 0)
        console.error("Unknown NUTS codes:", Array.from(_badids));

      const connexit = connections.exit().remove();

      // buuut don't go through the craziness if there's nothing to transition
      if (t.duration() === 0) return;

      const transitionConnections = (selection, newstuff) => {
        if (selection.empty()) return;

        // shallow clone the container
        const baselayer = container.node(),
          newlayer = baselayer.cloneNode(false);

        // insert the clone before the original if pending removal,
        // or after if the stuff is new
        baselayer.parentNode.insertBefore(
          newlayer,
          newstuff ? baselayer.nextSibling : baselayer,
        );

        // if exiting, this is a good time to add the fully-removed regions
        if (!newstuff) {
          rexit.each(function () {
            newlayer.appendChild(this);
          });
        }

        if (newstuff) newlayer.setAttribute("opacity", 0);

        // we're gonna move all the exit nodes under the new layer, but
        // we must clone each parent group as well, so...
        // instead of looping over connexit.nodes() and chasing each parent,
        // we'll using d3's beautifulous internals, which are structured
        // exactly the way we want them

        selection._groups.forEach(function (group, i) {
          // filter out empty elements
          group = group.filter((x) => true);
          if (!group.length) return;

          const parent = selection._parents[i],
            newparent = parent.cloneNode(false);
          newlayer.appendChild(newparent);

          for (const connection of group) {
            newparent.appendChild(connection);
          }
        });

        const exitfunc = function () {
          this.remove();
        };

        const enterfunc = function () {
          const parents = this.querySelectorAll("g");

          for (const parent of parents) {
            const selector = parent
              .getAttribute("class")
              .split(" ")
              .map((c) => "." + c)
              .join("");

            const baseparent = baselayer.querySelector("g" + selector);
            // also bring the parent to front, avoids some flicker
            baseparent.parentNode.appendChild(baseparent);

            while (parent.firstChild) {
              baseparent.appendChild(parent.firstChild);
            }
          }

          this.remove();
        };

        // we need to delay things a bit or d3 gets very confused
        this.$nextTick(() =>
          d3
            .select(newlayer)
            .classed("base", false)
            .classed(newstuff ? "new" : "old", true)
            .transition(t)
            .attr("opacity", newstuff ? this.default_opacity : 0)
            .on("end", newstuff ? enterfunc : exitfunc),
        );
      };

      // FIXME: there's something broken with the enter, leaving as is for now
      //transitionConnections(connentered, true)
      transitionConnections(connexit, false);
    },

    _domouse(over, ev, d) {
      const $super = BaseMap.methods._domouse.bind(this);
      const self = $super(over, ev, d);
      if (!self) return;
      if (self.classed("zero")) return;

      const t = this.getTransition(this.short_duration);
      const root = this.chart.select(".partnerships");
      // these will hold the region's connections, one per type
      let containers = root.selectAll(`g.${d.id}`);

      if (over) {
        if (containers.empty()) {
          // create the new containers and *copy* the connections under them
          // (while preserving their ancestry)

          const newlayers = [];
          for (const type of this.current_layers) {
            const base = root.select(`g.base.${type}`);

            const connections = base.selectAll("g").selectAll(`path.${d.id}`);

            if (connections.empty()) continue;

            const baselayer = base.node(),
              newlayer = baselayer.cloneNode(false);

            newlayer.classList.remove("base");
            newlayer.classList.add(d.id);
            baselayer.parentNode.appendChild(newlayer);

            connections._groups.forEach(function (group, i) {
              if (!group.length) return;

              const parent = connections._parents[i],
                newparent = parent.cloneNode(false);

              newlayer.appendChild(newparent);

              for (const connection of group) {
                newparent.appendChild(connection.cloneNode());
              }
            });

            newlayers.push(newlayer);
          }
          containers = d3.selectAll(newlayers);
        }
        // else they already exist, that is they weren't fully transitioned out.
        // fade them in
        containers.transition(t).attr("opacity", this.highlighted_opacity);

        // fade out the base layers
        for (const type of this.visible_layers)
          root
            .select(`g.base.${type}`)
            .transition(t)
            .attr("opacity", this.faded_opacity);
      } else {
        // (mouse out)

        // fade them out
        containers
          .transition(t)
          .attr("opacity", 0)
          .on("end", function () {
            this.remove();
          });

        // fade in the base layers
        for (const type of this.visible_layers)
          root
            .select(`g.base.${type}`)
            .transition(t)
            .attr("opacity", this.default_opacity);
      }
    },

    renderVisibleLayers(t) {
      if (t === undefined) t = this.getTransition();

      for (const layer of this.layers) {
        this.chart
          .select(`.partnerships > .${layer}`)
          .transition(t)
          .attr(
            "opacity",
            this.visible_layers.indexOf(layer) === -1
              ? 0
              : this.default_opacity,
          );
      }
    },

    handleLayers() {
      this.renderVisibleLayers();
    },

    handleFilter() {
      this.render();
    },
  },
};
</script>

<style lang="less">
@duration: 0.5s;
@short_duration: 0.2s;

.dataviz .viz.map.is-partners {
  .chart .regions {
    path {
      pointer-events: all;
    }

    path.donor {
      &:not(.zero):hover {
        stroke: #fff;
        stroke-opacity: 1;
      }
    }

    path.beneficiary,
    path.partner {
      &:not(.zero):hover {
        stroke: #000;
        stroke-opacity: 1;
      }
    }
  }

  .partnerships {
    pointer-events: none;
  }

  .selector {
    margin-bottom: 1rem;
    -js-display: flex;
    display: flex;
    @media (max-width: 800px) {
      display: block;
    }
    > label {
      display: inline-flex;
      @media (max-width: 800px) {
        -js-display: flex;
        display: flex;
      }
      margin-left: 1rem;
    }
  }

  input[type="checkbox"] {
    display: none;
  } /* to hide the checkbox itself */
  input[type="checkbox"] + label:before {
    display: inline-block;
  }

  input[type="checkbox"] + label {
    display: inline-block;
    border: solid #ddd;
    height: 19px;
    width: 19px;
    margin-right: 0.4rem;
    margin-top: -2px;
    position: relative;
  }

  input[type="checkbox"] + label:before {
    content: "" "";
    font-size: 2.5rem;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
  input[type="checkbox"]:checked + label:before {
    content: "✔\fe0e";
  } /* checked icon */
  #programmes {
    + label:before {
      color: #089900;
    }
  }

  #projects {
    + label:before {
      color: #e68a00;
    }
  }
}
</style>

