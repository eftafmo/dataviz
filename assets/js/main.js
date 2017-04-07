"use strict";

require("../css/normalize.css");
require("../css/main.css");

require("../js/header.js");

import * as d3 from "d3";
import {sankey as d3_sankey} from "d3-sankey";
import Vue from "vue";

var SidebarResults = new Vue({
  el: '#sidebar-results',
  data: {
    message: 'this is the header'
  }
});

// import MainApp from './MainApp.vue';

// new Vue({
//   el: '#content',
//   render: h => h(MainApp)
// });


require("../css/sankey.css");

let margin = {top: 10, right: 10, bottom: 10, left: 10},
    width = 700 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

let svg = d3.select("#content")//.append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("class", "sankey")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

let sankey = d3_sankey()
    .nodeWidth(15)
    .nodePadding(0)
    .size([width, height]);

const path = sankey.link();


const source_csv = '/api/allocation.csv';

d3.csv(source_csv, function(error, data) {
  const nodes = [],
        links = [];
  let _names = new Set();

  const color = d3.scaleOrdinal(d3.schemeCategory20),
        _format = d3.format(",.0f"),
        format = (d) => { return '€ ' + _format(d); };


  data.forEach(function (d) {
    _names.add(d.donor);
    _names.add(d.beneficiary);
    links.push({
      "source": d.donor,
      "target": d.beneficiary,
      "value": +d.amount,
    });
  });

  // d3 expects the nodes to be an array of objects,
  // and the links to be between the nodes' indexes.
  _names = Array.from(_names);
  _names.forEach(function(item, i) {
    nodes.push({
      "name": item,
    });
  });
  links.forEach(function (item) {
    item.source = _names.indexOf(item.source);
    item.target = _names.indexOf(item.target);
  });

  sankey
    .nodes(nodes)
    .links(links)
    .layout(0);

  let node = svg.append("g").selectAll(".node")
      .data(nodes)
      .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) {
        return "translate(" + d.x + "," + d.y + ")";
      });
  node.append("rect")
    .attr("height", function(d) {
      return d.dy;
    })
    .attr("width", sankey.nodeWidth())
    .style("fill", function(d) {
      return d.color = color(d.name.replace(/ .*/, ""));
    })
    .style("stroke", function(d) {
      return d3.rgb(d.color).darker(2);
    })
    .append("title")
    .text(function(d) {
      return `${d.name}\n${format(d.value)}`;
    });

  let link = svg.append("g").selectAll(".link")
      .data(links)
      .enter().append("path")
      .attr("class", "link")
      .attr("d", path)
      .style("stroke-width", function(d) {
        return Math.max(1, d.dy);
      })
      .sort(function(a, b) {
        return b.dy - a.dy;
      });
  link.append("title")
    .text(function(d) {
      return `${d.source.name} - ${d.target.name}\n${format(d.value)}`;
    });
});
