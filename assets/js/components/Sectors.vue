<template>
<div class="sectors-viz" :style="{minHeight: svgWidth + 'px'}">  <!-- todo: a better way to preserve container height? -->
  <svg :viewBox="`0 0 ${width} ${height}`">
    <defs>
      <filter id="dropshadow" x="-50%" y="-50%"  height="200%" width="200%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
        <feOffset dx="2" dy="2" />
        <feMerge>
          <feMergeNode />
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    <g class="chart" :transform="`translate(${margin + radius},${margin + radius})`">
    </g>
  </svg>
  <div class="legend" :style="{minHeight: svgWidth + 'px'}">
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
      >
        <a @click="click(sector)">
          {{ sector.data.name }} -

          <span :key="`v-${getLabelID(sector)}`">
            {{ format(sector.value) }}
          </span>
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
              v-show="filters.sector == sector.data.id"
              tag="ul"
              class="areas"
              name="item"
          >
            <li
                v-for="area in sector.children"
                v-if="area.value"
                :key="getLabelID(area)"
                :id="getLabelID(area)"
            >
              <a @click="click(area)">
                {{ area.data.name }} -

                <span :key="`v-${getLabelID(area)}`">
                  {{ format(area.value) }}
                </span>
              </a>
            </li>
          </transition-group>
        </transition>
      </li>
    </transition-group>
  </div>
</div>
</template>

<style lang="less">
.sectors-viz {
  svg {
    width: 50%;
    height: auto;
    display: block;
  }
  .legend {
    width: 50%;
    height: auto;
    position: relative;
    left: 50%;
    margin-top: -50%;
  }

  .chart path, .legend a {
    cursor: pointer;
  }

  .legend {

    /* animations:
     * -enter, -leave apply during the first frame only;
     * -*-active applies throughout the entire transition;
     * -*-to appplies during the last frame only;
     * -move applies only to items within a transition-group.

    /* these apply to all legend items, both sectors and areas.
     * useful when triggered by external filters.
     */

    .item-enter-active, .item-leave-active {
      transition: opacity 1s;
    }
    // (dis)appearing item fades in/out
    .item-enter, .item-leave-to {
      opacity: 0;
    }
    // remaining items move about
    // (this applies automatically when another item appears)
    .item-move {
      transition: transform 1s;
    }
    // setting this causes other items to get -move when one disappears
    .item-leave-active {
      position: absolute;
    }

    /* the areas list appears when filtering by parent sector
     */
    .areas-enter-active, .areas-leave-active {
      overflow: hidden;
      transition: height 1s, opacity 1s;
    }
    .areas-enter, .areas-leave-to {
      opacity: 0;
    }
    .areas-enter-to, .areas-leave {
      opacity: 1;
    }
  }


/*

.arc:hover, .arc.hovered { filter: url(#dropshadow); }
.label:hover rect, .label.hovered rect { filter: url(#dropshadow); }


  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  margin-bottom: 2rem;

  .sectors-close-indicator {
   margin-left: 5px;
   color: #ccc;
  }

  .label span {
      display: inline-block;
      margin-right: 5px;
      white-space: normal;
  }

  .label span:first-of-type {
      position: absolute;
      right: 100%;
      top: 0;
  }


  .label {
    font-size: 1.4rem;
    margin-bottom: .7rem;
    position: relative;
    white-space: nowrap;
    margin-left:15px;
    transition: all 400ms;
  }
  .sectors-legend-title {
      font-size: 1.6rem;
      margin-left: 0;
      margin-bottom: 1rem;
      cursor: pointer;
  }
  */
}


//
aside {display: none}

</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';

import BaseMixin from './mixins/Base';
import ChartMixin from './mixins/Chart';
import {SectorColours} from 'js/constants.js';


export default Vue.extend({
  mixins: [
    BaseMixin, ChartMixin,
  ],

  data() {
    return {
      width: 500,
      height: 500,

      margin: 10,

      // percentage of mid-donut void
      inner_radius: .65,

      duration: 500,
    };
  },

  computed: {
    data() {
      // TODO: avoid spurious run with empty data / track isReady()?
      //if (this.dataset === undefined) return;

      const tree = d3.hierarchy( { children: this.dataset } );

      // simplest way to get this recomputed on filter changes
      // is to access filter data right here.

      // filtering by sectors / areas makes items "disabled".
      const isEnabled = (this.filters.sector === null ?
        ( () => true ) :
        ( (d) => !d.allocation ? d.id == this.filters.sector :
                                 d.parent == this.filters.sector )
      );

      tree.sum( (d) => {
        // only last level has allocation
        if (!d.allocation) return 0;
        // filter out disabled items
        if (!isEnabled(d)) return 0;

        return d3.sum(
          d3.entries(d.allocation),
          (item) => {
            // allocation is grouped by FM, so filter if needed
            if (this.filters.fm
                && item.key != this.filters.fm) return 0;

            return item.value;
          }
        );
      } );

      return tree;
    },

    radius() {
      return Math.min(this.width, this.height) / 2 - this.margin;
    },

    _primary_colour() {
      const keys = [],
            values = [];
      for (let k in SectorColours) {
        keys.push(k);
        values.push(SectorColours[k]);
      }
      return d3.scaleOrdinal()
        .domain(keys)
        .range(values)
      // fail hard on missing values
        .unknown(null)
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
      return d3.arc()
        // the Math.min/max part  is needed to avoid funkiness for edge items
        .startAngle( (d) => Math.max(0, Math.min(2 * Math.PI, this._angle(d.x0))) )
        .endAngle( (d) => Math.max(0, Math.min(2 * Math.PI, this._angle(d.x1))) )
        //.outerRadius(this.radius)
        //.innerRadius(this.radius * this.inner_radius);
        //.outerRadius((d) => d.y0/2)
        //.innerRadius((d) => d.y1/2);
        .outerRadius((d) => d.depth == 1 ? this.radius * .75 : this.radius)
        .innerRadius((d) => d.depth == 1 ? this.radius * .5 : this.radius * .75);

    },
  },

  mounted() {
    this.root = null;
    this._secondary_colours = {};
    // this one's used during transitioning below
    this._areasCancelled = [];
  },

  methods: {
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

    processDataset(ds) {
      // add a reference to the parent sector to all areas
      // to keep track of filtering
      for (const s of ds) {
        for (const a of s.children) {
          a.parent = s.id;
        }
      }
      return ds;
    },

    _extract_coords: (d) => (
      {
        x0: d.x0, x1: d.x1,
        y0: d.y0, y1: d.y1,
        depth: d.depth,
      }
    ),

    _colour(d) {
      const func = (
        d.depth == 1 ?
          this._primary_colour :
          this._secondary_colours[d.parent.data.name]
      );
      return func(d.data.name);
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

    renderChart() {
      this.rendered = true;
      const $this = this,
            // flatten data
            data = this._partition(this.data)
                       .descendants()
                       .slice(1);
      const t = this.getTransition();


      // generate children colours. TODO: move to processDataset
      // or earlier. (fully pre-computed?)
      for (let d of this.data.children) {
        // TODO: make colours id-based
        const name = d.data.name;

        this._secondary_colours[name] = this._mkcolourscale(
          SectorColours[name], d.children.length
        );
      }

      const arcs = this.chart
	    .selectAll(".arc")
	    .data(data, this.getArcID); // JOIN

      const aentered = arcs.enter().append("path") // ENTER
        .each(function(d) {
	  // cache current coordinates
	  this._prev = $this._extract_coords(d);
	})
        .attr("id", this.getArcID)
	.attr("class", "arc")
	.attr("d", this._arc)
	.attr("fill", this._colour)
        // level 2 items are hidden and really hidden
        .attr("opacity", (d) => d.depth == 1 ? 1 : 1);

      const aexit = arcs.exit(); // EXIT

      /* transitions */
      // this stuff is complicated, each selection group will need its own transition
      // (actually ^^ that is a lie, there are no enter animations, and exit
      // never happens, but the code below is ready in case the logic changes).

      const transitioning = arcs // UPDATE
        .transition(t)
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
      // we also need to reset possibly grayed out areas,
      // and it needs to happen during this same transition §
      if (this._prevsector) {
        transitioning
          .filter(
            (d) => d.parent.data.id == this._prevsector
          )
          .attr("fill", this._colour);

        // we reset the prevsector during next tick only,
        // to avoid race conditions with handleFilterArea §
        this.$nextTick(
          () => this._prevsector = null
        );
      }

      // send new items to back so existing arcs cover them
      // during the transition and make them look animated
      aentered.lower(); // ENTER

      // send deleted items to back too
      aexit // EXIT
        .lower()
        .transition(t)
        .remove()


/*
        .transition(t)
        .attr("opacity", 0)
        //.remove();
*/

      /* events */
      aentered
        .on("click", this.click);
    },

    click(d) {
      const func = d.depth == 1 ? this.toggleSector : this.toggleArea;
      func(d.data.id, this);
    },

    toggleSector(s, etarget) {
      // always reset area on sector change, but do some special-casing §
      if(this.filters.area) {
        this._prevsector = this.filters.sector;
        this.filters.area = null;
      }
      this.filters.sector = this.filters.sector == s ?
                            null : s;
    },

    toggleArea(a, etarget) {
      if (!this.filters.sector) {
        console.error("Filtered by area without a sector. Impossible 1.")
        return;
      }
      this.filters.area = this.filters.area == a ?
                          null : a;
      // TODO: what if the area does not to the current sector belong?
      // TODO: we need a persistent array of PS / PAs
    },

    handleFilterSector(val, old) {
      // we'll need this below
      this.render();
    },

    handleFilterArea(val) {
      // don't go through a full render, as
      // this only needs to gray out sibling areas.

      // but WARNING, WARNING: transitions in d3 are element-exclusive, §
      // so in case the area filter was cleared by switching away
      // from the parent sector we can't handle this here.
      // we'll let the default sector-triggered render() to take care of it. §
      if (val === null && this._prevsector) {
        return;
      }

      if (val !== null && this.filters.sector === null)
        console.error("Filtered by area without a sector. Impossible 2.")

      const areas = this.chart
                        .selectAll(".arc")
                        .filter(
                          (d) => d.parent.data.id == this.filters.sector
                        );
      // TODO: unify this with the default colour func
      const colourfunc = (val === null ? this._colour :
        (d) => {
          const c = this._colour(d);
          if (d.data.id == this.filters.area) return c;

          // a simple(istic) algorithm to transform the colour to grayscale:
          // compute the average of r, g, b
          const r = d3.rgb(c),
                x = (r.r + r.g + r.b) / 3;
          return d3.rgb(x, x, x);
        }
      );

      areas
        .transition(this.getTransition())
        // TODO: if this was already grayed out it would be nice to pass
        // momentarily through the default colour
        .attr("fill", colourfunc);
    },

    handleFilterFm() {
      this.render();
    },



/*
      // prepare data hierarchy

      for (let node of this.root.descendants()) {
        node.data.enabled = true;
      }

    click(item) {
      const $this = this,
            root = $this.root;
      const _this = d3.select(item),
            node = _this.datum();

      //get the corresponding label for the arc when clicking an arc
      let _this_label = _this;
      if (item.classList.contains('arc')) {
       _this_label = $this._getOther(_this);
      }

      if (node.depth > 1) return;
      let _enable_nodes = node.descendants();
      for (let _node of root.descendants()) {
        if (_enable_nodes.indexOf(_node) != -1)
          _node.data.enabled = true;
        else
          _node.data.enabled = false;
      }

      // we need to set the arc below, or it will cover the secondaries
      const arc = _this.classed("arc") ? _this :
                  d3.select('#' + $this.getArcID(node));
      arc.lower();

      $this._labels
       .data($this.getRoot().descendants().slice(1))
       .on("click", function(d){
            if (d.depth == 1 && d.data.enabled == true) {
           $this.reset(item)
          }
        })
        .style("display", (d) => { return d.data.enabled ? "block" : "none"; })
        .style("opacity", function(d) { return !d.data.enabled ? 0 : this.opacity; })
        .attr('dummy', function(d){
        if (d.depth == 1 && d.data.enabled == true) {
            _this_label.attr('class','label sectors-legend-title');
            _this_label.append('span').text('×').attr('class', 'sectors-close-indicator');
          }
        });

     $this._arcs
	   .data($this.getRoot().descendants().slice(1))
      // enable stuff that's about to get animated, and hide the other stuff
      // abruptly, it looks better this way
        .style("display", (d) => { return d.data.enabled ? "inline" : "none"; })
      // reset that stuff's visibility while at it, but don't touch the rest
        .style("opacity", function(d) { return !d.data.enabled ? 0 : this.opacity; })
      // and then, transition to...
	     .transition()
        .duration(500)
      // .. full opacity / invisibility
        .attr("opacity", (d) => d.data.enabled ? 1 : 0)
      // and new coordinates`
      // finally, hide the level 1 as well
        .on("end", function(d) {
          if (d.depth == 1) {
            this.style.display = "none";
          }
        });

    },

    _getOther(obj) {
      // convenience function returning the label when given the arc
      // and vice-versa
      const selector = obj.classed('arc') ? this.getLabelID : this.getArcID;
      return d3.select("#" + selector(obj.datum()));
    },

    mouseover(item) {
      const $this = this,
            _this = d3.select(item),
            _other = $this._getOther(_this),
            arc = _this.classed('arc') ? _this : _other;

      // if we want pretty shadows the element needs to be brought to front
      arc.raise();
      // let the other be "hovered" too
      _other.classed("hovered", true);
    },
    mouseout(item) {
      const $this = this,
            _this = d3.select(item),
            _other = $this._getOther(_this);

      // make the other be unhovered
      _other.classed("hovered", false);
    },

    drawChart() {
      const $this = this,
      radius = $this.radius;

      // we need to perform our transitions on this current selection
      // or things get weird
      $this._arcs = arc;

      arc.append("title").text(function(d) { return d.data.name; });

      arc
        .on('click', function() { $this.click(this); })
        .on('mouseover', function() { $this.mouseover(this); })
        .on('mouseout', function() { $this.mouseout(this); })
    },

    drawLegend() {
      const $this = this,
	    label_size = $this.label_size,
	    label_spacing = $this.label_spacing;
      // draw the legend
      const label = $this.svg.select(".legend")
      .selectAll(".label")
        // we can access root directly here because we don't care about partitioning (yet?)
  	  .data($this.getRoot().descendants().slice(1))
  	  .enter().append("div")
  	  .attr("id", $this.getLabelID)
  	  .attr("class", "label")
      .style("opacity", (d) => d.depth == 1 ? 1 : 0)
      .style("display", (d) => d.depth == 1 ? "block" : "none");

      this._labels = label;
      label.append("span")
      .style('width', 1.7*label_size + 'px')
      .style('height', 1.7*label_size + 'px')
      .style('background', $this._colour)

      label.append('span')
      .attr('x', label_size + label_spacing)
      .attr('y', label_size)
      .text(function(d) { return d.data.name; });

      label
        .on('click', function() { $this.click(this); })
        .on('mouseover', function() { $this.mouseover(this); })
        .on('mouseout', function() { $this.mouseout(this); })
    },

    // WIP - reset the chart
    reset(item){
     const $this = this,
            root = $this.root;
      const _this = d3.select(item),
            node = _this.datum();
      if (node.depth > 1) return;

      let _enable_nodes = node.descendants();
      for (let _node of root.descendants()) {
          _node.data.enabled = false;
      }

      //get the corresponding label for the arc when clicking an arc
      let _this_label = _this;
      if (item.classList.contains('arc')) {
       _this_label = $this._getOther(_this);
      }

      $this._labels
        .data($this.getRoot().descendants().slice(1))
        .style("display", (d) => { return d.data.enabled ? "none" : "block"; })
        .style("opacity", function(d) { return !d.data.enabled ? this.opacity : 0; })
        .style('display', function(d){
           if (d.depth == 2 && d.data.enabled == false) {
            _this_label.attr('class','label');
            return "none"
          }
        });


      $this._labels
        .on('click', function() { $this.click(this); })
        .on('mouseover', function() { $this.mouseover(this); })
        .on('mouseout', function() { $this.mouseout(this); })

      //remove the X span from the label
      const close_indicator = $this.svg.select(".sectors-close-indicator")
      close_indicator.remove();

      $this._arcs
     .data($this.getRoot().descendants().slice(1))
      // enable stuff that's about to get animated, and hide the other stuff
        .style("display", (d) => { return d.data.enabled ? "none" : "inline"; })
      // reset that stuff's visibility while at it, but don't touch the rest
        .style("opacity", function(d) { return !d.data.enabled ? this.opacity : 0; })
      // and then, transition to...
       .transition()
        .duration(400)
      // .. full opacity / invisibility
        .attr("opacity", (d) => d.data.enabled ? 0 : 1)
        .attrTween('d', function(d,i) {
         const interpolate = d3.interpolate(
          this._prev, coords[i]
         );
          this._prev = interpolate(0);
          return function(x) {
            return $this._arc(interpolate(x));
          }
        })
         .on("end", function(d) {
          if (d.depth == 2) {
            this.style.display = "none";
          }
        });

    },
*/
  },
});

</script>
