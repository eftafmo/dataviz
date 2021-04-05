/*
 * based on d3-chord, which is BSD-licensed and
 * Copyright 2010-2016 Mike Bostock
 *
 * https://github.com/d3/d3-chord/blob/master/src/chord.js
 */

const pi = Math.PI
const tau = pi * 2
const max = Math.max
const min = Math.min

export default function () {
  let padding = 0
  let itemPadding = 0

  function chord (matrix) {
    const maxrad = pi - padding

    // start angles
    const as0 = tau - padding / 2
    const at0 = padding / 2

    // angle directions
    const asd = -1
    const atd = 1

    const ns = matrix.length
    const nt = matrix[0] === undefined ? 0 : matrix[0].length

    const chords = []

    const sourcegroups = chords.sources = new Array(ns)
    const targetgroups = chords.targets = new Array(nt)

    const ssubgroups = new Array(ns * nt)
    const tsubgroups = new Array(ns * nt)

    const sourceSums = new Array(ns)
    const targetSums = new Array(nt)

    let k
    let ks; let kt

    let x
    let x0
    let i
    let j

    j = -1; while (++j < nt) {
      targetSums[j] = 0
    }

    // Compute the sums.
    k = 0, i = -1; while (++i < ns) {
      x = 0, j = -1; while (++j < nt) {
        var v = matrix[i][j]
        targetSums[j] += v
        x += v
      }

      sourceSums[i] = x
      k += x
    }

    const _ns = sourceSums.filter((d) => d != 0).length
    const _nt = targetSums.filter((d) => d != 0).length

    // Convert the sum to scaling factors for [0, pi - padding].
    ks = max(0, maxrad - itemPadding * (_ns - 1)) / k
    kt = max(0, maxrad - itemPadding * (_nt - 1)) / k

    x = as0, i = -1; while (++i < ns) {
      x0 = x, j = -1; while (++j < nt) {
        var v = matrix[i][j]
        var a0 = x
        var a1 = x += asd * v * ks

        ssubgroups[i * nt + j] = {
          index: i,
          subindex: j,
          startAngle: min(a0, a1),
          endAngle: max(a0, a1),
          value: v
        }
      }

      sourcegroups[i] = {
        index: i,
        startAngle: min(x0, x),
        endAngle: max(x0, x),
        value: sourceSums[i]
      }

      if (x != x0) x += asd * itemPadding
    }

    x = at0, i = -1; while (++i < nt) {
      x0 = x, j = -1; while (++j < ns) {
        var v = matrix[j][i]
        var a0 = x
        var a1 = x += atd * v * kt

        tsubgroups[i * ns + j] = {
          index: i,
          subindex: j,
          startAngle: min(a0, a1),
          endAngle: max(a0, a1),
          value: v
        }
      }

      targetgroups[i] = {
        index: i,
        startAngle: min(x0, x),
        endAngle: max(x0, x),
        value: targetSums[i]
      }

      if (x != x0) x += atd * itemPadding
    }

    // Generate chords for each subgroup-subgroup link.
    i = -1; while (++i < ns) {
      j = -1; while (++j < nt) {
        const source = ssubgroups[i * nt + j]
        const target = tsubgroups[j * ns + i]
        chords.push({ source: source, target: target })
      }
    }

    return chords
  }

  chord.padding = function (_) {
    return arguments.length ? (padding = max(0, _), chord) : padding
  }

  chord.itemPadding = function (_) {
    return arguments.length ? (itemPadding = max(0, _), chord) : itemPadding
  }

  return chord
}
