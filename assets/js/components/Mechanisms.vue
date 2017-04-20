<template>
<div class="bar-thing">
  <svg :width="width" :height="height">
    <g class="chart"></g>
  </svg>
  <div v-if="data" class="legend">
    <ul class="fms clearfix">
      <li v-for="(fm, k, index) in fms"
          @click="toggleFm(fm, $event.target)"
          class="fm"
          :class="[fm.id, getFilterClass(fm)]"
      >
        <span class="value" :style="{color: colour(fm.id)}">{{ format(fm.value) }}</span>
        <span class="name">{{ fm.name }}</span>
      </li>
    </ul>
  </div>
</div>
</template>


<style>
.bar-thing,.fms {
  text-align: center;
}
.fm { cursor: pointer; }

.legend .fm {
  transition: all .5s ease;
}
.legend .fm.disabled {
  filter: grayscale(100%);
  opacity: 0.5;
}

.legend .fm.selected {
  text-shadow: 0 0 1px #999;
}


.fm {
  list-style-type: none;
  display: inline-block;
}

.fm:first-of-type {
  border-right: 1px solid #aaa;
  padding-right:2rem;
}

.fm:last-of-type {
  padding-left: 2rem;
}

.value {
  font-size: 1.8rem;
  font-weight: bold;
}

.fm .name {
  display: block;
}


</style>


<script>
import Vue from 'vue';
import * as d3 from 'd3';

import BaseMixin from './mixins/Base.vue';
import WithFMsMixin from './mixins/WithFMs.vue';

import FMs from 'js/constants/financial-mechanisms.json5';


export default Vue.extend({
  mixins: [BaseMixin, WithFMsMixin],

  props: {
    width: Number,
    // refers to the chart height only
    height: {
      type: Number,
      default: 30,
    },
    disabled_colour: {
      type: String,
      default: "#ccc",
    },
  },

  computed: {
    fms() {
      const fms = Object.assign({}, FMs);
      for (let fm in fms) {
        fms[fm].value = this.data[fm] || 0;
      }
      return fms;
    },
  },

  methods: {
    main() {
      this.renderChart();
    },

    renderChart() {
      const $this = this,
            _root = d3.select(this.$el),
            chart = _root.select("svg").select("g.chart");

      var x = d3.scaleLinear()
          .rangeRound([0, this.width])
          .domain([0, d3.sum(d3.values($this.data))]);

      const fms = chart
	    .selectAll(".fm")
            .data(d3.entries($this.data))
            .enter().append("rect")
            .attr("class", (d) => "fm " + d.key);

      fms
        .attr("x", (d) => 0)
        .attr("y", (d) => 0)
      // skip this here to transition it below
      //.attr("width", (d) => x(d.value))
        .attr("height", "100%")
        .attr("transform", (d, i) => {
          // draw the second bar from right to left
          if (i == 1) return (
            `scale(-1,1) translate(-${this.width},0)`
          );
        })
        .attr("fill", (d) => $this.colour(d.key))
        .transition()
        .duration(500)
        .attr("width", (d) => x(d.value));

      fms
        .append("title").text((d) => $this.format(d.value));
      fms
        .append("desc").text((d) => $this.fms[d.key].name);

      fms
        .on("click", function (d) {
          $this.toggleFm($this.fms[d.key], this);
        });

      // remember the current selection, we'll use it for transitionsc
      this._chart_fms = fms;
    },

    getFmId(fm) {
      // silly utility func to return FM's id regardless of input type

      // is this the id already?
      if (typeof fm == "string") return fm;
      if (typeof fm == "object") {
        // regular fm object?
        if (fm.id) return fm.id;
        // a result of d3.entries()?
        if (fm.key) return fm.key;
      }
      throw `Can't get FM id for ${typeof fm}.`
    },

    toggleFm(fm, etarget) {
      const fmid = this.getFmId(fm);
      this.filters.fm = this.filters.fm == fmid ?
                         null : fmid;
    },

    getFilterClass(fm) {
      if (!this.filters.fm)
        return;

      if (this.isSelected(fm))
        return "selected";

      if (this.isDisabled(fm))
        return "disabled";
    },

    isSelected(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm == this.getFmId(fm);
    },
    isDisabled(fm) {
      if (!this.filters.fm) return;
      return this.filters.fm != this.getFmId(fm);
    },

    handleFilterFm(val, old) {
      // transition the chart to disabled / selected.
      // (the legend is handled by vue.)

      const $this = this;

      // TODO: handle the case when !this.isReady()
      this._chart_fms
        .transition()
        .duration(500)
        .attr("fill", (d) => (this.isDisabled(d.key) ?
                              $this.disabled_colour : $this.colour(d.key))
        );
    },
  },
});

</script>
