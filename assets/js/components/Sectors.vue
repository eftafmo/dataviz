<template>
<div class="sectors-viz clearfix" :style="{minHeight: svgWidth + 'px'}">  <!-- todo: a better way to preserve container height? -->
<chart-container :width="width" :height="height">
  <svg :viewBox="`0 0 ${width} ${height}`">
    <g class="chart" :transform="`translate(${margin + radius},${margin + radius})`">
    </g>
  </svg>
  <transition appear>
  <svg v-if="filters.sector" :key="filters.sector" class="sector-icon">
    <use :xlink:href="`#${get_image(filters.sector)}`" />
  </svg>
  </transition>
</chart-container>
  <div class="legend" v-if="hasData" :style="{minHeight: svgWidth + 'px'}">
    <!-- much repetition here, but not worth doing a recursive component -->
    <transition-group
        tag="ul"
        class="sectors"
        name="item"
    >
      <li
          v-for="sector in data.children"
          v-if="sector.value"
          :key="getLabelID(sector)"
          :id="getLabelID(sector)"
          :class="{selected: isSelectedSector(sector)}"
      >
        <a @click="click(sector)"
           @mouseenter="isSelectedSector(sector) ? null : highlight(sector)"
           @mouseleave="isSelectedSector(sector) ? null : unhighlight(sector)"
        >
          <span :style="{background: sector.data.colour}"></span>
          <span>
            {{ sector.data.name }}
          </span>
          <span
              v-show="filters.sector != sector.data.id"
              :key="`v-${getLabelID(sector)}`">
            {{ value(sector) }}
          </span>
          <span
              v-if="isSelectedSector(sector)"
              class="icon icon-close"
          />
        </a>

        <transition
            v-on:before-enter="areasBeforeEnter"
            v-on:before-leave="areasBeforeLeave"
            v-on:after-enter="areasReset"
            v-on:after-leave="areasReset"
            v-on:enter-cancelled="areasCancelled"
            v-on:leave-cancelled="areasCancelled"
            name="areas"
        >
          <transition-group
              v-show="isSelectedSector(sector)"
              tag="ul"
              class="areas"
              name="item"
          >
            <li
                v-for="area in sector.children"
                v-if="area.value"
                :key="getLabelID(area)"
                :id="getLabelID(area)"
                :class="{ inactive: !isActiveArea(area) }"
            >
              <a @click="click(area)"
                 @mouseenter="highlight(area)"
                 @mouseleave="unhighlight(area)"
              >
                <span :style="{background: area.data.colour}"></span>
                <span>
                  {{ area.data.name }}
                </span>
                <span :key="`v-${getLabelID(area)}`">
                  {{ value(area) }}
                </span>
              </a>
            </li>
          </transition-group>
        </transition>
      </li>
    </transition-group>
  </div>
  <div v-if="hasData" class="dropdown">
    <dropdown filter="sector" title="Select a sector" :items="filtered_dataset"></dropdown>
  </div>
</div>
</template>

<style lang="less">
.sectors-viz {
  // defs
  @text-colour: #444;
  // these need to be synced with js
  @duration: .5s;
  @short_duration: .25s;
  @inactive_opacity: .7;

  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  @media(min-width: 1000px) and (max-width: 1400px) {
    display: block;
  }

  svg {
    width: 100%;
  }

  .chart-container {
    width: 40%;
    height: auto;
    display: block;
    margin-right: 3rem;
    min-width: 200px;

    @media (min-width: 1000px) and (max-width: 1400px) {
      float: left;
    }

    @media (min-width:1400px), (max-width:700px) {
       width: 50%;
       margin-right: 0;
    }
  }

  .sector-icon {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%,-50%);
    width: 50%;
    height: 50%;
    display: block;
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
    @media (min-width:1400px), (max-width:1025px) {
      width: 100%;
      margin-top: 1rem;
    }
    @media (min-width: 1000px) and (max-width: 1400px) {
      float: left;
    }
  }

  .chart path, .legend a {
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

          span:first-child {
            width: 2rem;
            height: 2rem;
            flex: 0 0 2rem;
          }

          &:hover {
            span.icon-close {
              color: #000;
              font-weight: bold;
            }
          }
        }

        &.selected span.icon-close {
          font-size: 120%;
        }

        a {
          display: flex;
          padding: .4rem;
          text-decoration: none;
          color: @text-colour;
          border: 1px solid transparent;
          border-radius: .2rem;
          //transition: border-color @short_duration;
          transition: padding @short_duration;

          // not using :hover here because it's handled by the script
          &.hovered {
            border-color: #9ae;
          }

          * {
            display: block;
            flex-grow: 1;
            margin: 0 0.2rem 0 0.2rem;
          }
          span:first-child {
            flex: 0 0 1.8rem;
            width: 1.8rem;
            height: 1.8rem;
            margin-left: 0;
            margin-right: 0.6rem;
            transition: width @short_duration, height @short_duration, flex @short_duration;
          }
          *:last-child {
            margin-right: 0;
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

    .item-enter-active, .item-leave-active {
      transition: opacity @duration;
    }
    // (dis)appearing item fades in/out
    .item-enter, .item-leave-to {
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
    .areas-enter-active, .areas-leave-active {
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

  .d3-tip.sect:after {
    top: 19px;
    transform: rotate(180deg);
  }
</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';
import debounce from 'lodash.debounce';
import merge from 'lodash.merge';
import {colour2gray, slugify} from 'js/lib/util';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import WithSectors from './mixins/WithSectors';
import WithTooltipMixin from './mixins/WithTooltip';


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
    WithSectors,
    WithTooltipMixin,
  ],

  data() {
    return {
      width: 500,
      height: 500,

      margin: 10,

      // percentage of mid-donut void
      inner_radius: .65,
    };
  },

  beforeCreate() {
    // cache for the sector / area names & colors ¤
    this._sectortree = null;
    // a queue to know which sector's child areas should be disappeared §
    this._prevsector = [];
  },

  computed: {
    filtered_sectors() {
      // filter dataset by everything except sector / area
      const _filters = d3.keys(this.filters)
                         .filter((f) => f != 'sector' && f != 'area');
      const dataset = this.filter(this.dataset, _filters);
      const aggregated = this.aggregate(
        dataset,
        ['sector', 'area', 'fm'],
        [
          'allocation',
          //'bilateral_allocation',
          'project_count',
          //'project_count_positive',
          //'project_count_ended',
          //{source: 'sector', destination: 'sectors', type: String},
        ],
        false
      );

      const out = {}
      for (const sname in aggregated) {
        const areas = aggregated[sname],
              sid = slugify(sname);

        let sector = out[sid];
        if (sector === undefined)
          sector = out[sid] = {
            id: sid,
            name: sname,
            children: {},
            project_count: 0,
            total: 0,
          };

        for (const aname in areas) {
          const fms = areas[aname],
                aid = slugify(aname)

          let area = sector.children[aid];
          if (area === undefined)
            area = sector.children[aid] = {
              id: aid,
              name: aname,
              // TODO: do we actually need this split by fm?
              allocation: {},
              // TODO: so... keep the project count per fm, or total?
              project_count: 0,
              total: 0,
            };

          for (const fmname in fms) {
            const fm = fms[fmname];

            area.allocation[fmname] = fm.allocation;
            area.total += fm.allocation;
            area.project_count += fm.project_count;
            sector.total += fm.allocation;
            sector.project_count += fm.project_count;
          }
        }
      }

      return out;
    },

    filtered_dataset() {
      return d3.values(this.filtered_sectors);
    },

    data() {
      // TODO: generate this on the server instead ¤
      let sectortree = this._sectortree;
      if (sectortree === null) {
        // pre-generate the tree, without any allocation data
        sectortree = this._sectortree = Object.assign({}, this.SECTORS);

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
              children: {},
              colour: '#555',
            };

          let children = sector.children;
          if (children === undefined)
            children = sector.children = {};

          let area = children[aid];
          if (area === undefined)
            area = children[aid] = {
              id: aid,
              name: a,
              allocation: {},
            };
        }

        // final touches
        for (const sid in sectortree) {
          const sector = sectortree[sid],
                colour = sector.colour,
                areas = d3.values(sector.children);

          // add a backreference to the parent sector for all areas
          // and generate area colors
          const colourscale = this._mkcolourscale(colour, areas.length);

          for (const area of areas) {
            area.parentname = sector.name;
            area.colour = colourscale(area.id);
          }
        }
      }
      // done pre-generation

      // we need to deep-copy the tree and merge it with the actual data
      const sectors = merge({}, sectortree, this.filtered_sectors);


      // finally, using d3's hierarchy makes working with trees easy
      const tree = d3.hierarchy(
        { children: sectors },
        // the default accessor function looks for arrays of children,
        // but we have an object tree
        (d) => d3.values(d.children)
      );

      // filtering by sectors / areas makes items "disabled".
      const isEnabled = (d) => {
        if (this.filters.sector === null) return true;
        if (d.allocation === undefined) return this._isSelectedSector(d.name);
        return this._isSelectedSector(d.parentname);
      };

      // tell the hierarchy object how to calculate sums
      tree.sum( (d) => {
        // only last level has allocation
        if (!d.allocation) return 0;
        // filter out disabled items
        if (!isEnabled(d)) return 0;

        return d3.sum(
          d3.entries(d.allocation),
          (item) => item.value
        );
      } );

      return tree;
    },

    radius() {
      return Math.min(this.width, this.height) / 2 - this.margin;
    },

    _partition() {
      return d3.partition().size([this.radius * 2, this.radius * 2]);
    },
    _angle() {
      return d3.scaleLinear()
               .domain([0, this.radius * 2])
               .range([0, Math.PI * 2]);
    },
    _arc() {
      return this._mkarc(this.radius,
                         this.radius * this.inner_radius);
    },
    _arcLarge() {
      return this._mkarc(this.radius + this.margin,
                         this.radius * this.inner_radius);
    },

  },

  mounted() {
    this.root = null;
    // this one's used during transitioning below
    this._areasCancelled = [];
  },

  methods: {
    value(item) {
      // the value displayed in legend
      return this.currency(item.value);
    },

    areasBeforeEnter(el) {
      // get height from a clone, it's safer
      const c = el.cloneNode(true);
      c.style.visibility = "hidden";
      c.style.removeProperty("display");
      c.style.height = "auto";
      el.parentNode.appendChild(c);
      const h = c.clientHeight;
      c.remove();

      // start from 0, but only if we didn't interrupt another transition
      const _idx = this._areasCancelled.indexOf(el);
      if (_idx === -1)
        el.style.height = "0px";
      else
        this._areasCancelled.splice(_idx, 1);


      // using setTimeout is the only way to get predictable results
      setTimeout( () => el.style.height = h + "px", 1);
    },

    areasBeforeLeave(el) {
      // start from current height (unless another transition is in progress)
      const _idx = this._areasCancelled.indexOf(el);
      if (_idx === -1)
        el.style.height = el.clientHeight + "px";
      else
        this._areasCancelled.splice(_idx, 1);

      setTimeout( () => el.style.height = "0px", 1);
    },

    areasReset(el) {
      el.style.removeProperty("height");
    },

    areasCancelled(el, x){
      this._areasCancelled.push(el);
    },

    _extract_coords: (d) => (
      {
        x0: d.x0, x1: d.x1,
        y0: d.y0, y1: d.y1,
        depth: d.depth,
      }
    ),

    _mkarc(outerradius, innerradius) {
      const arc = d3.arc()
        // the Math.min/max part  is needed to avoid funkiness for edge items
        .startAngle( (d) => Math.max(0, Math.min(2 * Math.PI, this._angle(d.x0))) )
        .endAngle( (d) => Math.max(0, Math.min(2 * Math.PI, this._angle(d.x1))) )
        .outerRadius(outerradius);

      if (innerradius)
        arc.innerRadius(innerradius);

      return arc;
    },

    _mkcolourscale: (colour, length) => {
      if (length == 1) return d3.scaleOrdinal([colour]);

      const _c = d3.hsl(colour);
      let start = d3.hsl(_c.h, _c.s, _c.l, _c.opacity),
	  end = d3.hsl(_c.h, _c.s, _c.l, _c.opacity);

      const _delta = d3.scaleLinear()
            // these values are rather arbitrary but they look pretty
	    .domain([2, 5])
	    .range([0.1, 0.5])
	    .clamp(true)
      (length);

      // make the starting colour _delta% more saturated,
      start.s = Math.min(1, start.s + start.s * _delta);
      // and slightly darker
      start.l = Math.max(0, start.l - start.l * _delta);
      // and the ending colour a bit lighter,
      end.l = Math.min(0.95, end.l + end.l * _delta);

      const _range = d3.range(length);
      let _scale = d3.scaleLinear()
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
    getArcID(node) { return "a-" + this._getID(node); },
    getLabelID(node) { return "l-" + this._getID(node); },

    get_image(sname) { return slugify(sname); },

    tooltipTemplate(d) {
      // TODO: such horribleness.
      const thing = d.depth == 1 ? "priority sector" : "programme area";

      return `
        <div class="title-container">
          <span>${ d.data.name }</span>
        </div>
        <ul>
          <li>${ this.currency(d.value) } grant allocation</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },

    createTooltip() {
       // add tooltip
      let tip = d3.tip()
          .attr('class', 'd3-tip sect')
          .html(this.tooltipTemplate)
          .offset([15,30])
          .direction('s');

       this.tip = tip;
       this.chart.call(this.tip)
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
            // flatten data
            data = this._partition(this.data)
                       .descendants()
                       .slice(1);
      const t = this.getTransition();

      const arcs = this.chart
	    .selectAll("g.arc > path")
	    .data(data, this.getArcID); // JOIN

      const aentered = arcs.enter() // ENTER
        // the container:
        .append("g")
        .attr("id", this.getArcID)
        .attr("class", "arc")
        .attr("fill", (d) => d.data.colour )
        // level 2 items are hidden
        .attr("opacity", (d) => d.depth == 2 ? 0 : null )
        // and really hidden
        .style("display", (d) => d.depth == 2 ? "none" : null )

        // the arc:
        .append("path")
        .each(function(d) {
          // cache current coordinates
          this._prev = $this._extract_coords(d);
        })
        .attr("d", this._arc)

        // events
        .on("click", this.click)
        .on("mouseenter", this.highlight)
        .on("mouseleave", this.unhighlight)
        .on('mouseover', this.tip.show)
        .on('mouseout', this.tip.hide);

      /* transitions */
      // NOTE: there is no ENTER or EXIT, all items are persistent ¤

      const transitioning = arcs // UPDATE
        .transition(t)
        // avoid other transitions while this runs ¬
        .on("start",
            () => this._transitioning = true )
        .on("end",
            () => this._transitioning = false )

        // we can't use this._arc directly as it yields funky distortions,
        // so we need a custom interpolation. attrTween to the rescue
        .attrTween('d', function(d) {
	  const interpolate = d3.interpolate(
	    this._prev, $this._extract_coords(d)
	  );
          this._prev = interpolate(0);

          return function(x) {
            return $this._arc(interpolate(x));
          }
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
          this.renderWait.min, {maxWait: this.renderWait.max}
        );
      renderer();
    },

    _renderAreasStuff() {
      // the real areas stuff implementation
      const currsector = this.filters.sector,
            prevsector = (
              this._prevsector.length && this._prevsector[0] != currsector ?
                this._prevsector.shift() : null // §
            );

      const t = this.getTransition();

      const areas = this.chart
                        .selectAll("g.arc")
                        .filter( (d) => d.depth == 2 );

      if (currsector) {
        areas.filter( (d) => this.isSelectedSector(d.parent) )
          .transition(t)
          .style("display", null) // null undoes any other value
          .attr("opacity", 1)
          .attr("fill", (d) => {
            const c = d.data.colour;
            if (this.filters.area === null) return c;
            if (this.isActiveArea(d)) return c;
            // TODO: if this was already grayed out it would be nice to pass
            // momentarily through the default colour
            return colour2gray(c, this.inactive_opacity);
          })
      }

      if (prevsector) {
        areas.filter( (d) => d.parent.data.name == prevsector )
          .transition(t)
          .style("display", null) // null undoes any other value
          .attr("opacity", 0)
          // reset colours to default
          .attr("fill", (d) => d.data.colour )
          .on("end", function() { this.style.display = "none"; })
      }
    },

    click(d) {
      const func = d.depth == 1 ? this.toggleSector : this.toggleArea;
      func(d, this);
    },

    _highlight(d, yes) {
      // avoid funny race conditions ¬
      if(this._transitioning) return;

      const arc = this.getArcID(d),
            label = this.getLabelID(d);

      const arcfunc = yes ? this._arcLarge : this._arc;

      d3.select(this.$el).select(`#${label} > a`)
        .classed("hovered", yes);

      d3.select(this.$el).select(`#${arc} > path`)
        .transition(this.getTransition(this.short_duration))
        .attr("d", arcfunc)
    },

    highlight(d) {
      this._highlight(d, true);
    },

    unhighlight(d) {
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
      return this.isSelectedSector(a.parent) &&
             this.filters.area == a.data.name;
    },

    toggleSector(s, etarget) {
      const sname = s.data.name;
      this.filters.sector = this.filters.sector == sname ?
                            null : sname;
    },

    toggleArea(a, etarget) {
      if (!this.filters.sector) {
        console.error("Filtered by area without a sector. Impossible 1.")
        return;
      }
      const aname = a.data.name;
      this.filters.area = this.filters.area == aname ?
                          null : aname;
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
        console.error("Filtered by area without a sector. Impossible 2.")
      // this only needs to gray out sibling areas.
      this.renderAreasStuff();
    },
  },
});

</script>
