<template>
<div class="sectors-viz">
  <svg :width="width" :height="height">
    <defs>
      <filter id="dropshadow" x="-50%" y="-50%"  height="200%" width="200%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="3">
        </feGaussianBlur>
        <feComponentTransfer>
          <feFuncA type="linear" slope="0">
            <animate id="dropshadow-anim-in"
              attributeName="slope" attributeType="XML"
              begin="indefinite" dur="0.1" end="indefinite" fill="freeze"
              from="0" to="1"
            />
          </feFuncA>
        </feComponentTransfer>
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
  <div class="legend" :transform="`translate(${radius * 2 + radius / 2},${margin})`">
  </div>
</div>
</template>

<style lang="less">
.chart {}
.legend {}
.arc, .label { cursor: pointer; }
.arc:hover, .arc.hovered { filter: url(#dropshadow); }
.label:hover rect, .label.hovered rect { filter: url(#dropshadow); }
.sectors-viz {
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

  .legend {
      max-width: 600px;
      margin-left: 5rem;
  }
}

</style>

<script>
import Vue from 'vue';
import * as d3 from 'd3';

import {SectorColours} from 'js/constants.js';


// https://github.com/wbkd/d3-extended (..?)
d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
    const lastChild = this.parentNode.lastChild;
    if (lastChild && lastChild != this) {
      this.parentNode.appendChild(this);
    }
  });
};
d3.selection.prototype.moveToBack = function() {
  return this.each(function() {
    const firstChild = this.parentNode.firstChild;
    if (firstChild && firstChild != this) {
      this.parentNode.insertBefore(this, firstChild);
    }
  });
};
d3.selection.prototype.moveBelow = function() {
  return this.each(function() {
    const previousSibling = this.previousSibling;
    if (previousSibling) {
      this.parentNode.insertBefore(this, previousSibling);
    }
    this.parentNode.appendChild(this);
  });
};

var coords=[];

export default Vue.extend({
  props: {
    datasource: String,
    width: Number,
    height: Number,
    margin: {
      type: Number,
      default: 10,
    },
    label_size: {
      type: Number,
      default: 10,
    },
    label_spacing: {
      type: Number,
      default: 5,
    },
  },
  computed: {
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
      const $this = this;
      return d3.arc()
        .startAngle(function(d) { return $this._angle(d.x0) })
        .endAngle(function(d) { return $this._angle(d.x1) })
        .outerRadius($this.radius)
        .innerRadius($this.radius * 65 / 100);
        //.outerRadius((d) => d.y0/2)
        //.innerRadius((d) => d.y1/2);
    },
    _format: () => d3.format(",d"),
  },

  mounted() {
    this.svg = d3.select(this.$el);
    this.root = null;
    this._secondary_colours = {};
    this.doStuff();
  },

  methods: {
    setUp(data) {
      // prepare data hierarchy
      this.root = d3.hierarchy({children: data});
      for (let node of this.root.descendants()) {
        node.data.enabled = true;
      }

      // generate children colours
      for (let d of data) {
        // TODO: make colours id-based
        this._secondary_colours[d.name] = this._mkcolourscale(
          SectorColours[d.name], d.children.length
        );
      }
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

    _colour(d) {
      const func = (
        d.depth == 1 ?
          this._primary_colour :
          this._secondary_colours[d.parent.data.name]
      );
      return func(d.data.name);
    },

    getArcID: (node) => `a${node.depth}-${node.data.id}`,
    getLabelID: (node) => `l${node.depth}-${node.data.id}`,

    getRoot() {
      // sum needs to be recomputed every time,
      this.root.sum((d) => {
        if (!d.enabled || !d.allocation) return 0;
        // TODO: apply filtering
        return d3.sum(d3.values(d.allocation));
      });

      // along with re-partitioning
      this._partition(this.root);

      return this.root;
    },

    _extract_coords: (d) => (
	   {x0: d.x0, x1: d.x1, y0: d.y0, y1: d.y1}
    ),

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
      arc.moveToBack();

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
        .attrTween('d', function(d) {
	       const interpolate = d3.interpolate(
		      this._prev, $this._extract_coords(d)
	       );
          this._prev = interpolate(0);
          return function(x) {
            return $this._arc(interpolate(x));
          }
        })
      // finally, hide the level 1 as well
        .on("end", function(d) {
          if (d.depth == 1) {
            this.style.display = "none";
          }
        });

    },

    _getAnim: () => {
      const anim = document.getElementById('dropshadow-anim-in'),
	    parent = anim.parentNode;
      // make sure the animation is stopped
      parent.appendChild(parent.removeChild(anim));
      return anim;
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
      arc.moveToFront();
      // let the other be "hovered" too
      _other.classed("hovered", true);
      // and start the shadow animation
      $this._getAnim().beginElement();
    },
    mouseout(item) {
      const $this = this,
            _this = d3.select(item),
            _other = $this._getOther(_this);

      // makethe other be unhovered
      _other.classed("hovered", false);
       // and reset the shadow animation
      $this._getAnim();
    },

    drawChart() {
      const $this = this,
      radius = $this.radius;
      const arc = $this.svg.select("g.chart")
	    .selectAll(".arc")
      // always use $this.getRoot() to make sure the data is properly partitioned
	    .data($this.getRoot().descendants().slice(1))
	    .enter().append("path")
	    .each(function(d,i) {
	      // cache current coordinates
	      this._prev = $this._extract_coords(d);
        coords[i]=this._prev;
	    })
	    .attr("id", $this.getArcID)
	    .attr("class", "arc")
	    .attr("d", $this._arc)
	    .attr("fill", $this._colour)
      // level 2 items are hidden and really hidden
      .attr("opacity", (d) => d.depth == 1 ? 1 : 0)
      .style("display", (d) => d.depth == 1 ? "inline" : "none")

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

    doStuff() {
      const $this = this;
      d3.json(this.datasource, function(error, data) {
	if (error) throw error;
        $this.setUp(data);
        $this.drawChart();
        $this.drawLegend();
      });
    },
  },
  watch: {
    datasource: {
      handler: 'doStuff',
      deep: true,
    },
  },
});

</script>
