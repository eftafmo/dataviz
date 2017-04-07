<template>
<svg class="pie-thing" :width="width" :height="height">
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
  <g class="legend" :transform="`translate(${radius * 2 + radius / 2},${radius / 2})`">
  </g>
</svg>
</template>

<style>
.chart {}
.legend {}
.arc, .label { cursor: pointer; }
.arc:hover, .arc.hovered { filter: url(#dropshadow); }
.label:hover rect, .label.hovered rect { filter: url(#dropshadow); }

</style>

<script>
/*
import Vue from 'vue';
import * as d3 from 'd3';
*/


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

//export default Vue.extend({
module.exports = {
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
  data: () => ({
    // TODO: move this someplace nice
    colours: {
      "environmental-protection-and-management": "#90A522",
      "climate-change": "#F58345",
      "carbon-capture-and-storage": "#75489D",
      "green-industry-innovation": "#C4016A",
      "human-and-social-development": "#00AFF0",
      "civil-society": "#0BA245",
      "decent-work-and-tripartite-dialogue": "#6D7D94",
      "protecting-cultural-heritage": "#692800",
      "research-and-scholarship": "#F2C009",
      "justice-and-home-affairs": "#096C93",

      "technical-assistance": "#cccccc",
      "other": "#cccccc",
    },
  }),
  computed: {
    radius() {
      return Math.min(this.width, this.height) / 2 - this.margin;
    },

    _primary_colour() {
      const keys = [],
            values = [];
      for (let k in this.colours) {
        keys.push(k);
        values.push(this.colours[k]);
      }
      return d3.scaleOrdinal()
        .domain(keys)
        .range(values)
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
        .innerRadius($this.radius * 70 / 100);
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
        this._secondary_colours[d.id] = this._mkcolourscale(
          this.colours[d.id], d.children.length
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
          this._secondary_colours[d.parent.data.id]
      );
      return func(d.data.id);
    },

    getLabelID(item) {
      return `l${this._uid}-${item}`;
    },
    getArcID: (node) => `a${node.depth}-${node.data.id}`,
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

      if (node.depth > 1) return;

      let _enable_nodes = node.descendants();
      for (let _node of root.descendants()) {
        if (_enable_nodes.indexOf(_node) != -1)
          _node.data.enabled = true;
        else
          _node.data.enabled = false;
      }

      // we need to set ourselves below, or we'll cover the secondaries
      _this.moveToBack();

      $this._arcs
	.data($this.getRoot().descendants().slice(1))
      // enable stuff that's about to get animated, and hide the other stuff
      // abruptly, it looks better this way
        .style("display", (d) => { return d.data.enabled ? "inline" : "none"; })
      // reset that stuff's visibility while at it, but don't touch the rest
        .style("opacity", function(d) { return !d.data.enabled ? 0 : this.opacity; })

      // and then, transition to...
	.transition()
        .duration(750)
      // .. full opacity / invisibility
        .attr("opacity", (d) => d.data.enabled ? 1 : 0)
      // and new coordinates
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
          if (d.depth == 1) this.style.display = "none";
        });
    },

    _getAnim: () => {
      const anim = document.getElementById('dropshadow-anim-in'),
	    parent = anim.parentNode;

      // this makes sure the animation is really stopped
      parent.removeChild(anim);
      parent.appendChild(anim);

      return anim;
    },

    mouseover(item) {
      d3.select(item).moveToFront();
      this._getAnim().beginElement();
    },
    mouseout(item) {
      this._getAnim();
    },

    drawChart() {
      const $this = this,
	    radius = $this.radius;

      const arc = $this.svg.select("g.chart")
	    .selectAll(".arc")
	    .data($this.getRoot().descendants().slice(1))
	    .enter().append("path")
	    .each(function(d) {
	      // cache current coordinates
	      this._prev = $this._extract_coords(d);
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
      this._arcs = arc;

      arc
        .on('click', function(d, i, nodes) { $this.click(this); })
        .on('mouseover', function() { $this.mouseover(this); })
        .on('mouseout', function() { $this.mouseout(this); })

	.append("title").text(function(d) { return d.data.name; });
    },

    drawLegend() {
      const $this = this,
	    label_size = this.label_size,
	    label_spacing = this.label_spacing;
      const root = this.root;
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
};

</script>
