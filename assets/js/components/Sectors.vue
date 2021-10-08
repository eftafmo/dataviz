<template>
  <div
    :class="classNames"
    class="clearfix"
    :style="{ minHeight: chartWidth + 'px' }"
  >
    <embeddor :period="period" tag="sectors" :svg-node="$refs.svgEl" />
    <!-- todo: a better way to preserve container height? -->
    <slot v-if="!embedded" name="title"></slot>
    <dropdown
      v-if="rendered"
      filter="sector"
      title="No filter selected"
      :items="filtered_dataset"
    ></dropdown>
    <div class="chart-wrapper">
      <chart-container :width="width" :height="height">
        <svg
          ref="svgEl"
          :viewBox="`0 0 ${width} ${height}`"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g
            class="chart"
            :transform="`translate(${margin + radius},${margin + radius})`"
          ></g>

          <transition appear>
            <image
              v-if="filters.sector"
              :key="filters.sector"
              :x="width / 4"
              :y="height / 4"
              :width="width / 2"
              :height="height / 2"
              class="sector-icon"
              :href="sectorImage(filters.sector)"
            />
          </transition>
        </svg>
      </chart-container>
      <div
        v-if="hasData"
        ref="legend"
        class="legend"
        :style="{ minHeight: minHeight + 'px' }"
      >
        <!-- much repetition here, but not worth doing a recursive component -->
        <transition-group tag="ul" class="sectors" name="item">
          <li
            v-for="sector in data.children.filter((d) => d.value)"
            :id="getLabelID(sector)"
            :key="getLabelID(sector)"
            :class="{ selected: isSelectedSector(sector) }"
          >
            <a
              @click="click({}, sector)"
              @mouseenter="
                isSelectedSector(sector) ? null : highlight({}, sector)
              "
              @mouseleave="
                isSelectedSector(sector) ? null : unhighlight({}, sector)
              "
            >
              <span :style="{ background: sector.data.color }"></span>
              <span>
                {{ sector.data.name }}
              </span>
              <span
                v-show="filters.sector != sector.data.id"
                :key="`v-${getLabelID(sector)}`"
                class="sector-allocation"
              >
                {{
                  isSelectedSector(sector)
                    ? displayLong(sector)
                    : display(sector)
                }}
              </span>
              <span v-if="isSelectedSector(sector)" class="icon icon-cross" />
            </a>

            <transition
              name="areas"
              @before-enter="areasBeforeEnter"
              @before-leave="areasBeforeLeave"
              @after-enter="areasReset"
              @after-leave="areasReset"
              @enter-cancelled="areasCancelled"
              @leave-cancelled="areasCancelled"
            >
              <transition-group
                v-show="isSelectedSector(sector)"
                tag="ul"
                class="areas"
                name="item"
              >
                <li
                  v-for="area in sector.children.filter((d) => d.value)"
                  :id="getLabelID(area)"
                  :key="getLabelID(area)"
                  :class="{ inactive: !isActiveArea(area) }"
                >
                  <a
                    @click="click({}, area)"
                    @mouseenter="highlight({}, area)"
                    @mouseleave="unhighlight({}, area)"
                  >
                    <span :style="{ background: area.data.color }"></span>
                    <span>
                      {{ area.data.name }}
                    </span>
                    <span :key="`v-${getLabelID(area)}`">
                      {{ display(area) }}
                    </span>
                  </a>
                </li>
              </transition-group>
            </transition>
          </li>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";
import d3tip from "d3-tip";
import debounce from "lodash.debounce";
import merge from "lodash.merge";
import { color2gray, slugify } from "@js/lib/util";

import Chart from "./Chart";
import WithSectors from "./mixins/WithSectors";
import WithTooltipMixin from "./mixins/WithTooltip";
import Embeddor from "./includes/Embeddor";

export default {
  components: { Embeddor },
  extends: Chart,
  type: "sectors",

  mixins: [WithSectors, WithTooltipMixin],

  data() {
    return {
      width: 500,
      height: 500,

      margin: 10,

      // percentage of mid-donut void
      inner_radius: 0.65,
      minHeight: null,
    };
  },

  computed: {
    filtered_sectors() {
      const aggregated = this.aggregated;

      const out = {};
      for (const sname in aggregated) {
        const sid = slugify(sname),
          areas = aggregated[sname];

        const sector = (out[sid] = {
          id: sid,
          name: sname,
          children: {},
        });

        for (const aname in areas) {
          const aid = slugify(aname),
            area = (sector.children[aid] = areas[aname]);

          Object.assign(area, {
            id: aid,
            name: aname,
          });

          delete area.sector;
          delete area.area;
        }
      }

      return out;
    },

    filtered_dataset() {
      return Object.values(this.filtered_sectors);
    },

    data() {
      // TODO: generate this on the server instead ¤
      let sectortree = this._sectortree;
      if (sectortree === null) {
        // pre-generate the tree, without any allocation data
        sectortree = Object.assign({}, this.SECTORS);

        for (const d of this.dataset) {
          const s = d.sector,
            a = d.area,
            sid = slugify(s),
            aid = slugify(a);

          let sector = sectortree[sid];
          // this.SECTORS should contain everything already, but one never knows
          if (sector === undefined)
            sector = sectortree[sid] = {
              id: sid,
              name: s,
              color: "#555",
            };

          let children = sector.children;
          if (children === undefined) children = sector.children = {};

          let area = children[aid];
          if (area === undefined)
            area = children[aid] = {
              id: aid,
              name: a,
            };
        }

        // final touches
        for (const sid in sectortree) {
          const sector = sectortree[sid],
            color = sector.color,
            areas =
              sector.children === undefined
                ? []
                : Object.values(sector.children);

          // add a backreference to the parent sector for all areas
          // and generate area colors
          const colorscale = this._mkcolorscale(color, areas.length);

          for (const area of areas) {
            area.parentid = sector.id;
            area.parentname = sector.name;
            area.color = colorscale(area.id);
          }
        }
      }
      // done pre-generation ¤

      // we need to deep-copy the tree and merge it with the actual data
      const sectors = merge({}, sectortree, this.filtered_sectors);

      // finally, using d3's hierarchy makes working with trees easy
      const tree = d3.hierarchy(
        { children: sectors },
        // the default accessor function looks for arrays of children,
        // but we have an object tree
        (d) => (d.children === undefined ? [] : Object.values(d.children))
      );

      // tell the hierarchy object how to calculate sums
      tree.sum(this.valuefunc);

      return tree;
    },

    radius() {
      return Math.min(this.width, this.height) / 2 - this.margin;
    },

    _partition() {
      return d3.partition().size([this.radius * 2, this.radius * 2]);
    },
    _angle() {
      return d3
        .scaleLinear()
        .domain([0, this.radius * 2])
        .range([0, Math.PI * 2]);
    },
    _arc() {
      return this._mkarc(this.radius, this.radius * this.inner_radius);
    },
    _arcLarge() {
      return this._mkarc(
        this.radius + this.margin,
        this.radius * this.inner_radius
      );
    },
  },

  watch: {
    filters: {
      deep: true,
      handler() {
        this.calcHeight();
      },
    },
    chartWidth: {
      handler() {
        this.minHeight = 0;
      },
    },
  },

  beforeCreate() {
    // cache for the sector / area names & colors ¤
    this._sectortree = null;
    // a queue to know which sector's child areas should be disappeared §
    this._prevsector = [];
  },

  created() {
    const cols = ["sector", "area"];

    for (const col of cols) {
      // don't filter by sector / area
      const fid = this.filter_by.indexOf(col);
      if (fid !== -1) this.filter_by.splice(fid, 1);

      // but group by them
      this.aggregate_by.push(col);

      // (and don't aggregate them)
      const aid = this.aggregate_on.findIndex((x) => x.source == col);
      if (aid !== -1) this.aggregate_on.splice(aid, 1);
    }
  },

  mounted() {
    this.root = null;
    // this one's used during transitioning below
    this._areasCancelled = [];
  },

  methods: {
    isRoot(d) {
      // the root node of the data tree
      return d.id === undefined;
    },

    isRogue(d) {
      // regue sector without values, due to how the sector list is pre-built
      // note that there are rogue areas too, but we can only tell those apart
      // in local code
      return d.children === undefined && d.parentname === undefined;
    },

    isSector(d) {
      return d.children !== undefined;
    },

    // filtering by sectors / areas makes items "disabled".
    isEnabled(d) {
      if (this.filters.sector === null) return true;
      if (this.isSector(d)) return this._isSelectedSector(d.name);
      return this._isSelectedSector(d.parentname);
    },

    // the value used in pie-chart calculations
    valuefunc(d) {
      // only leaf nodes have value data
      if (this.isRoot(d) || this.isRogue(d) || this.isSector(d)) return 0;

      // filter out disabled items
      if (!this.isEnabled(d)) return 0;

      return d.net_allocation;
    },

    // the value displayed for legend items
    display(item) {
      return this.currency(item.value);
    },
    displayLong(item) {
      return this.currency(item.value) + " net allocation";
    },

    areasBeforeEnter(el) {
      // get height from a clone, it's safer
      const c = el.cloneNode(true);
      c.style.visibility = "hidden";
      c.style.removeProperty("display");
      c.style.height = "auto";
      el.parentNode.appendChild(c);
      const h = c.clientHeight;
      el.parentNode.removeChild(c);

      // start from 0, but only if we didn't interrupt another transition
      const _idx = this._areasCancelled.indexOf(el);
      if (_idx === -1) el.style.height = "0px";
      else this._areasCancelled.splice(_idx, 1);

      // using setTimeout is the only way to get predictable results
      setTimeout(() => (el.style.height = h + "px"), 1);
    },

    areasBeforeLeave(el) {
      // start from current height (unless another transition is in progress)
      const _idx = this._areasCancelled.indexOf(el);
      if (_idx === -1) el.style.height = el.clientHeight + "px";
      else this._areasCancelled.splice(_idx, 1);

      setTimeout(() => (el.style.height = "0px"), 1);
    },

    areasReset(el) {
      el.style.removeProperty("height");
    },

    areasCancelled(el, x) {
      this._areasCancelled.push(el);
    },

    _extract_coords: (d) => ({
      x0: d.x0,
      x1: d.x1,
      y0: d.y0,
      y1: d.y1,
      depth: d.depth,
    }),

    _mkarc(outerradius, innerradius) {
      const arc = d3
        .arc()
        // the Math.min/max part  is needed to avoid funkiness for edge items
        .startAngle((d) =>
          Math.max(0, Math.min(2 * Math.PI, this._angle(d.x0)))
        )
        .endAngle((d) => Math.max(0, Math.min(2 * Math.PI, this._angle(d.x1))))
        .outerRadius(outerradius);

      if (innerradius) arc.innerRadius(innerradius);

      return arc;
    },

    _mkcolorscale: (color, length) => {
      if (length == 1) return d3.scaleOrdinal([color]);

      const _c = d3.hsl(color);
      let start = d3.hsl(_c.h, _c.s, _c.l, _c.opacity),
        end = d3.hsl(_c.h, _c.s, _c.l, _c.opacity);

      const _delta = d3
        .scaleLinear()
        // these values are rather arbitrary but they look pretty
        .domain([2, 5])
        .range([0.1, 0.5])
        .clamp(true)(length);

      // make the starting color _delta% more saturated,
      start.s = Math.min(1, start.s + start.s * _delta);
      // and slightly darker
      start.l = Math.max(0, start.l - start.l * _delta);
      // and the ending color a bit lighter,
      end.l = Math.min(0.95, end.l + end.l * _delta);

      const _range = d3.range(length);
      let _scale = d3
        .scaleLinear()
        .domain([0, length - 1])
        .range([start, end])
        .interpolate(d3.interpolateHsl);

      return d3.scaleOrdinal(d3.range(length).map(_scale));
    },

    _getID(node) {
      // include parent id, because area clash makes boom
      const parent = node.depth == 2 ? this._getID(node.parent) + "_" : "";
      return parent + node.data.id;
    },
    getArcID(node) {
      return "a-" + this._getID(node);
    },
    getLabelID(node) {
      return "l-" + this._getID(node);
    },

    tooltipTemplate(ev, d) {
      // TODO: such horribleness.
      let thing = "programme area",
        bss = d.data.beneficiaries,
        prgs = d.data.programmes;

      if (d.depth == 1) {
        thing = "sector";
        bss = new Set();
        prgs = new Set();

        for (const c of d.children) {
          if (c.data.beneficiaries)
            for (const bs of c.data.beneficiaries.values()) bss.add(bs);
          if (c.data.programmes)
            for (const prg of c.data.programmes.values()) prgs.add(prg);
        }
      }

      const num_bs = bss.size;
      const num_prg = prgs.size;

      return (
        `
        <div class="title-container">
          <span>${d.data.name}</span>
        </div>
        <ul>
          <li>${this.display(d)} net allocation</li>
          <li>${num_bs} ` +
        this.singularize(`Beneficiary States`, num_bs) +
        `</li>
          <li>${num_prg}  ` +
        this.singularize(`programmes`, num_prg) +
        `</li>
        </ul>
        <span class="action">Click to filter by ${thing}</span>
      `
      );
    },

    createTooltip() {
      // add tooltip
      let tip = d3tip()
        .attr("class", "dataviz dataviz-tooltip sect")
        .html(this.tooltipTemplate)
        .offset([15, 30])
        .direction("s");

      this.tip = tip;
      this.chart.call(this.tip);
    },

    /*
       NOTE:
       The following transitions happen:
       - (1) arc lenghts
       - (2) colors (and visibility and opacity)

       Due to transitions being element-exclusive in d3, and to avoid
       needlessly re-rendering everything,
       - (1) happen on <path> elements,
       - (2) happen on their <g> containers.

       (1) are triggered
         - by filtering on FM and BS (obviously, data changes),
         - when filtering by a PS: the other sectors turn to 0, while
           its children PAs fill up the 360 degrees.

       (2) are triggered only when filtering by a PA: its siblings will
           be grayed out.

       (and well, there's also (3) - arc dimension change during mouseover)

     */
    renderChart() {
      const $this = this,
        currsector = this.filters.sector,
        // flatten data
        data = this._partition(this.data).descendants().slice(1);
      const t = this.getTransition();

      // make sure getting instantiated with a filter works properly
      if (!this.rendered && currsector) this._prevsector.push(currsector);

      const arcs = this.chart
        .selectAll("g.arc > path")
        .data(data, this.getArcID); // JOIN

      const aentered = arcs
        .enter() // ENTER
        // the container:
        .append("g")
        .attr("id", this.getArcID)
        .attr("class", "arc");

      aentered.filter((d) => d.depth == 1).attr("fill", (d) => d.data.color);

      const areas = aentered.filter((d) => d.depth == 2);
      // areas are normally hidden, unless filtered by sector.
      // they're also normally colored.
      if (!currsector) {
        areas
          .attr("opacity", 0)
          .style("display", "none")
          .attr("fill", (d) => d.data.color);
      } else {
        areas
          .attr("opacity", (d) => (this.isSelectedSector(d.parent) ? 1 : 0))
          .style("display", (d) =>
            this.isSelectedSector(d.parent) ? null : "none"
          );

        if (this.filters.area === null) {
          areas.attr("fill", (d) => d.data.color);
        } else {
          areas.attr("fill", (d) => {
            const c = d.data.color;
            if (this.isActiveArea(d)) return c;
            return color2gray(c, this.inactive_opacity);
          });
        }
      }

      // the arc:
      aentered
        .append("path")
        .each(function (d) {
          // cache current coordinates
          this._prev = $this._extract_coords(d);
        })
        .attr("d", this._arc)

        // events
        .on("click", this.click)
        .on("mouseenter", this.highlight)
        .on("mouseleave", this.unhighlight)
        .on("mouseover", this.tip.show)
        .on("mouseout", this.tip.hide);

      /* transitions */
      // NOTE: there is no ENTER or EXIT, all items are persistent ¤

      const transitioning = arcs // UPDATE
        .transition(t)
        // avoid other transitions while this runs ¬
        .on("start", () => (this._transitioning = true))
        .on("end", () => (this._transitioning = false))

        // we can't use this._arc directly as it yields funky distortions,
        // so we need a custom interpolation. attrTween to the rescue
        .attrTween("d", function (d) {
          const interpolate = d3.interpolate(
            this._prev,
            $this._extract_coords(d)
          );
          this._prev = interpolate(0);

          return function (x) {
            return $this._arc(interpolate(x));
          };
        });
    },

    renderAreasStuff() {
      // "renders" areas' opacity and colors.
      // debounce the actual implementation because it can happen both during
      // area filtering and sector filtering.
      let renderer = this._areaStuffRenderer;
      if (renderer === undefined)
        renderer = this._areaStuffRenderer = debounce(
          this._renderAreasStuff,
          this.renderWait.min,
          { maxWait: this.renderWait.max }
        );
      renderer();
    },

    _renderAreasStuff() {
      // the real areas stuff implementation
      const currsector = this.filters.sector,
        prevsector =
          this._prevsector.length && this._prevsector[0] != currsector
            ? this._prevsector.shift()
            : null; // §

      const t = this.getTransition();

      const areas = this.chart.selectAll("g.arc").filter((d) => d.depth == 2);

      if (currsector) {
        areas
          .filter((d) => this.isSelectedSector(d.parent))
          .transition(t)
          .style("display", null) // null undoes any other value
          .attr("opacity", 1)
          .attr("fill", (d) => {
            const c = d.data.color;
            if (this.filters.area === null) return c;
            if (this.isActiveArea(d)) return c;
            // TODO: if this was already grayed out it would be nice to pass
            // momentarily through the default color
            return color2gray(c, this.inactive_opacity);
          });
      }

      if (prevsector) {
        areas
          .filter((d) => d.parent.data.name == prevsector)
          .transition(t)
          .style("display", null) // null undoes any other value
          .attr("opacity", 0)
          // reset colors to default
          .attr("fill", (d) => d.data.color)
          .on("end", function () {
            this.style.display = "none";
          });
      }
    },

    click(ev, d) {
      const func = d.depth == 1 ? this.toggleSector : this.toggleArea;
      func(d, this);
    },

    _highlight(d, yes) {
      // avoid funny race conditions ¬
      if (this._transitioning) return;

      const arc = this.getArcID(d),
        label = this.getLabelID(d);

      const arcfunc = yes ? this._arcLarge : this._arc;

      d3.select(this.$el).select(`#${label} > a`).classed("hovered", yes);

      d3.select(this.$el)
        .select(`#${arc} > path`)
        .transition(this.getTransition(this.short_duration))
        .attr("d", arcfunc);
    },

    highlight(ev, d) {
      this._highlight(d, true);
    },

    unhighlight(ev, d) {
      this._highlight(d, false);
    },

    _isSelectedSector(sname) {
      // avoid a mess caused by differing capitalization until we switch to ids
      return slugify(this.filters.sector) == slugify(sname);
    },

    // NOTE: these functions will take a d3.hierarchy node as argument,
    // so we must access everything via element.data
    isSelectedSector(s) {
      if (!this.filters.sector) return;
      return this._isSelectedSector(s.data.name);
    },

    isActiveArea(a) {
      if (!this.filters.area) return true;
      return (
        this.isSelectedSector(a.parent) && this.filters.area == a.data.name
      );
    },

    toggleSector(s, etarget) {
      const sname = s.data.name;
      this.filters.sector = this.filters.sector == sname ? null : sname;
    },

    toggleArea(a, etarget) {
      if (!this.filters.sector) {
        console.error("Filtered by area without a sector. Impossible 1.");
        return;
      }
      const aname = a.data.name;
      this.filters.area = this.filters.area == aname ? null : aname;
      // TODO: what if the area does not to the current sector belong?
      // TODO: take into account the persistent array of PS / PAs. ¤
    },

    handleFilterSector(val, old) {
      // remember this soon-to-be previous sector.
      // (it will be removed from the queue during handling of areas §)
      if (val) this._prevsector.push(val);

      // always reset area on sector change
      this.filters.area = null;

      // TODO: share a transition instance between these.
      this.render();
      this.renderAreasStuff();
    },

    handleFilterArea(val) {
      if (val !== null && this.filters.sector === null)
        console.error("Filtered by area without a sector. Impossible 2.");
      // this only needs to gray out sibling areas.
      this.renderAreasStuff();
    },

    calcHeight() {
      if (window.matchMedia("(min-width: 768px)").matches) {
        const $this = this;
        const legend = this.$refs.legend;
        if (!legend) return;
        let prevHeight = legend.clientHeight;
        this.minHeight = Math.max($this.minHeight, prevHeight);
      } else return;
    },
  },
};
</script>

<style lang="less">
.dataviz .viz.sectors {
  // defs
  @text-color: #444;
  // these need to be synced with js
  @duration: 0.5s;
  @short_duration: 0.25s;
  @inactive_opacity: 0.7;

  position: relative;
  @media (min-width: 1000px) and (max-width: 1400px) {
    display: block;
    .chart-container {
      -js-display: flex;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  }

  .chart-wrapper {
    clear: right;
  }

  svg {
    width: 100%;
  }

  h2 {
    margin-bottom: 0;
  }

  .chart-container {
    width: 40%;
    height: auto;
    display: block;
    margin-right: auto;
    margin-left: auto;
    min-width: 200px;

    @media (min-width: 1000px) and (max-width: 1400px) {
      float: left;
    }

    @media (min-width: 1400px), (max-width: 700px) {
      width: 50%;
      margin-right: auto;
      margin-left: auto;
    }
  }

  .sector-icon {
    &.v-enter-active,
    &.v-leave-active {
      transition: opacity @duration;
    }

    &.v-enter,
    &.v-leave-to {
      opacity: 0;
    }
    &.v-enter-to,
    &.v-leave {
      opacity: 1;
    }
  }

  .legend {
    width: 55%;
    display: block;
    height: auto;
    position: relative;
    @media (min-width: 1400px), (max-width: 1025px) {
      width: 100%;
      margin-top: 1rem;
    }
    @media (min-width: 1000px) and (max-width: 1400px) {
      float: left;
    }
  }

  .chart path,
  .legend a {
    cursor: pointer;
  }

  .legend {
    ul {
      &.areas {
        margin-left: 2.6rem;
        // the vertical spacing has to be on the inside
        // because we animate height
        li:first-of-type {
          padding-top: 1rem;
        }
      }
      list-style-type: none;
      padding: 0;
      font-size: 1.4rem;

      li {
        margin-bottom: 0.3rem;

        &.selected > a {
          font-size: 120%;
          border-style: none;
          padding: 0;

          .sector-allocation {
            text-align: right;
            white-space: nowrap;
          }

          & > span:first-child {
            width: 2rem;
            height: 2rem;
            flex: 0 0 2rem;
          }

          &:hover {
            span.icon {
              color: #000;
              font-weight: bold;
            }
          }
        }

        a {
          display: flex;
          align-items: center;
          padding: 0.4rem;
          text-decoration: none;
          color: @text-color;
          border: 1px solid transparent;
          border-radius: 0.2rem;
          //transition: border-color @short_duration;
          transition: padding @short_duration;

          // not using :hover here because it's handled by the script
          &.hovered {
            border-color: #50b9ff;
          }

          * {
            display: block;
            flex-grow: 1;
            margin: 0 0.2rem 0 0.2rem;
          }
          & > span:first-child {
            flex: 0 0 1.8rem;
            width: 1.8rem;
            height: 1.8rem;
            margin-left: 0;
            margin-right: 0.6rem;
            transition: width @short_duration, height @short_duration,
              flex @short_duration;
          }
          & > *:last-child {
            margin-right: 0;
            margin-left: 0.2rem;
            flex-grow: unset;
            text-align: right;
          }
        }
      }
    }

    .areas li {
      transition: all @duration;
    }
    .areas li.inactive {
      filter: grayscale(100%);
      opacity: @inactive_opacity;
    }

    /* animations:
     * -enter, -leave apply during the first frame only;
     * -*-active applies throughout the entire transition;
     * -*-to appplies during the last frame only;
     * -move applies only to items within a transition-group.

    /* these apply to all legend items, both sectors and areas.
     * useful when triggered by external filters.
     */

    .item-enter-active,
    .item-leave-active {
      transition: opacity @duration;
    }
    // (dis)appearing item fades in/out
    .item-enter,
    .item-leave-to {
      opacity: 0;
    }
    // remaining items move about
    // (this applies automatically when another item appears)
    .item-move {
      transition: transform @duration;
    }
    // setting this causes other items to get -move when one disappears
    .item-leave-active {
      position: absolute;
    }

    /* the areas list appears when filtering by parent sector
     */
    .areas-enter-active,
    .areas-leave-active {
      overflow: hidden;
      transition: height @duration, opacity @duration;
    }
    /*
    // things seem to look better without opacity
    // TODO: test
    .areas-enter, .areas-leave-to {
      opacity: 0;
    }
    .areas-enter-to, .areas-leave {
      opacity: 1;
    }
    */
  }
}

.dataviz-tooltip.sect:after {
  top: 19px;
  transform: rotate(180deg);
}
</style>
