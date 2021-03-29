/*
 * based on d3-chord, which is BSD-licensed and
 * Copyright 2010-2016 Mike Bostock
 *
 * https://github.com/d3/d3-chord/blob/master/src/chord.js
 */

var pi = Math.PI,
  tau = pi * 2,
  max = Math.max,
  min = Math.min;

export default function () {
  var padding = 0,
    itemPadding = 0;

  function chord(matrix) {
    var maxrad = pi - padding,
      // start angles
      as0 = tau - padding / 2,
      at0 = padding / 2,
      // angle directions
      asd = -1,
      atd = 1,
      ns = matrix.length,
      nt = matrix[0] === undefined ? 0 : matrix[0].length,
      chords = [],
      sourcegroups = (chords.sources = new Array(ns)),
      targetgroups = (chords.targets = new Array(nt)),
      ssubgroups = new Array(ns * nt),
      tsubgroups = new Array(ns * nt),
      sourceSums = new Array(ns),
      targetSums = new Array(nt),
      k,
      ks,
      kt,
      x,
      x0,
      i,
      j;

    j = -1;
    while (++j < nt) {
      targetSums[j] = 0;
    }

    // Compute the sums.
    (k = 0), (i = -1);
    while (++i < ns) {
      (x = 0), (j = -1);
      while (++j < nt) {
        var v = matrix[i][j];
        targetSums[j] += v;
        x += v;
      }

      sourceSums[i] = x;
      k += x;
    }

    var _ns = sourceSums.filter((d) => d != 0).length,
      _nt = targetSums.filter((d) => d != 0).length;

    // Convert the sum to scaling factors for [0, pi - padding].
    ks = max(0, maxrad - itemPadding * (_ns - 1)) / k;
    kt = max(0, maxrad - itemPadding * (_nt - 1)) / k;

    (x = as0), (i = -1);
    while (++i < ns) {
      (x0 = x), (j = -1);
      while (++j < nt) {
        var v = matrix[i][j],
          a0 = x,
          a1 = (x += asd * v * ks);

        ssubgroups[i * nt + j] = {
          index: i,
          subindex: j,
          startAngle: min(a0, a1),
          endAngle: max(a0, a1),
          value: v,
        };
      }

      sourcegroups[i] = {
        index: i,
        startAngle: min(x0, x),
        endAngle: max(x0, x),
        value: sourceSums[i],
      };

      if (x != x0) x += asd * itemPadding;
    }

    (x = at0), (i = -1);
    while (++i < nt) {
      (x0 = x), (j = -1);
      while (++j < ns) {
        var v = matrix[j][i],
          a0 = x,
          a1 = (x += atd * v * kt);

        tsubgroups[i * ns + j] = {
          index: i,
          subindex: j,
          startAngle: min(a0, a1),
          endAngle: max(a0, a1),
          value: v,
        };
      }

      targetgroups[i] = {
        index: i,
        startAngle: min(x0, x),
        endAngle: max(x0, x),
        value: targetSums[i],
      };

      if (x != x0) x += atd * itemPadding;
    }

    // Generate chords for each subgroup-subgroup link.
    i = -1;
    while (++i < ns) {
      j = -1;
      while (++j < nt) {
        var source = ssubgroups[i * nt + j],
          target = tsubgroups[j * ns + i];
        chords.push({ source: source, target: target });
      }
    }

    return chords;
  }

  chord.padding = function (_) {
    return arguments.length ? ((padding = max(0, _)), chord) : padding;
  };

  chord.itemPadding = function (_) {
    return arguments.length ? ((itemPadding = max(0, _)), chord) : itemPadding;
  };

  return chord;
}
