// import flexibility from 'flexibility'
// flexibility(document.documentElement);
import 'classlist-polyfill'
import 'form-association-polyfill'
import 'url-polyfill'
require('es6-promise').polyfill()

if (!Object.assign) {
  Object.defineProperty(Object, 'assign', {
    enumerable: false,
    configurable: true,
    writable: true,
    value: function (target) {
      'use strict'
      if (target === undefined || target === null) {
        throw new TypeError('Cannot convert first argument to object')
      }

      const to = Object(target)
      for (let i = 1; i < arguments.length; i++) {
        let nextSource = arguments[i]
        if (nextSource === undefined || nextSource === null) {
          continue
        }
        nextSource = Object(nextSource)

        const keysArray = Object.keys(Object(nextSource))
        for (let nextIndex = 0, len = keysArray.length; nextIndex < len; nextIndex++) {
          const nextKey = keysArray[nextIndex]
          const desc = Object.getOwnPropertyDescriptor(nextSource, nextKey)
          if (desc !== undefined && desc.enumerable) {
            to[nextKey] = nextSource[nextKey]
          }
        }
      }
      return to
    }
  })
}

/*
  the following functions are courtesy of MDN, released in the public domain.
  https://developer.mozilla.org/en-US/docs/MDN/About#Copyrights_and_licenses
*/
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/find
if (!Array.prototype.find) {
  Object.defineProperty(Array.prototype, 'find', {
    value: function (predicate) {
      // 1. Let O be ? ToObject(this value).
      if (this == null) {
        throw new TypeError('"this" is null or not defined')
      }

      const o = Object(this)

      // 2. Let len be ? ToLength(? Get(O, "length")).
      const len = o.length >>> 0

      // 3. If IsCallable(predicate) is false, throw a TypeError exception.
      if (typeof predicate !== 'function') {
        throw new TypeError('predicate must be a function')
      }

      // 4. If thisArg was supplied, let T be thisArg; else let T be undefined.
      const thisArg = arguments[1]

      // 5. Let k be 0.
      let k = 0

      // 6. Repeat, while k < len
      while (k < len) {
        // a. Let Pk be ! ToString(k).
        // b. Let kValue be ? Get(O, Pk).
        // c. Let testResult be ToBoolean(? Call(predicate, T, « kValue, k, O »)).
        // d. If testResult is true, return kValue.
        const kValue = o[k]
        if (predicate.call(thisArg, kValue, k, o)) {
          return kValue
        }
        // e. Increase k by 1.
        k++
      }

      // 7. Return undefined.
      return undefined
    }
  })
}

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/fill
if (!Array.prototype.fill) {
  Object.defineProperty(Array.prototype, 'fill', {
    value: function (value) {
      // Steps 1-2.
      if (this == null) {
        throw new TypeError('this is null or not defined')
      }

      const O = Object(this)

      // Steps 3-5.
      const len = O.length >>> 0

      // Steps 6-7.
      const start = arguments[1]
      const relativeStart = start >> 0

      // Step 8.
      let k = relativeStart < 0
        ? Math.max(len + relativeStart, 0)
        : Math.min(relativeStart, len)

      // Steps 9-10.
      const end = arguments[2]
      const relativeEnd = end === undefined
        ? len
        : end >> 0

      // Step 11.
      const final = relativeEnd < 0
        ? Math.max(len + relativeEnd, 0)
        : Math.min(relativeEnd, len)

      // Step 12.
      while (k < final) {
        O[k] = value
        k++
      }

      // Step 13.
      return O
    }
  })
}

// https://developer.mozilla.org/en-US/docs/Web/API/ChildNode/remove
// from:https://github.com/jserz/js_piece/blob/master/DOM/ChildNode/remove()/remove().md
(function (arr) {
  arr.forEach(function (item) {
    if (item.hasOwnProperty('remove')) {
      return
    }
    Object.defineProperty(item, 'remove', {
      configurable: true,
      enumerable: true,
      writable: true,
      value: function remove () {
        this.parentNode.removeChild(this)
      }
    })
  })
})([Element.prototype, CharacterData.prototype, DocumentType.prototype])

// https://tc39.github.io/ecma262/#sec-array.prototype.findIndex
if (!Array.prototype.findIndex) {
  Object.defineProperty(Array.prototype, 'findIndex', {
    value: function (predicate) {
      // 1. Let O be ? ToObject(this value).
      if (this == null) {
        throw new TypeError('"this" is null or not defined')
      }

      const o = Object(this)

      // 2. Let len be ? ToLength(? Get(O, "length")).
      const len = o.length >>> 0

      // 3. If IsCallable(predicate) is false, throw a TypeError exception.
      if (typeof predicate !== 'function') {
        throw new TypeError('predicate must be a function')
      }

      // 4. If thisArg was supplied, let T be thisArg; else let T be undefined.
      const thisArg = arguments[1]

      // 5. Let k be 0.
      let k = 0

      // 6. Repeat, while k < len
      while (k < len) {
        // a. Let Pk be ! ToString(k).
        // b. Let kValue be ? Get(O, Pk).
        // c. Let testResult be ToBoolean(? Call(predicate, T, « kValue, k, O »)).
        // d. If testResult is true, return k.
        const kValue = o[k]
        if (predicate.call(thisArg, kValue, k, o)) {
          return k
        }
        // e. Increase k by 1.
        k++
      }

      // 7. Return -1.
      return -1
    }
  })
}
/*!
 * Stickyfill -- `position: sticky` polyfill
 * v. 1.1.4 | https://github.com/wilddeer/stickyfill
 * Copyright Oleg Korsunsky | http://wd.dizaina.net/
 *
 * MIT License
 */
(function (doc, win) {
  const watchArray = []
  let scroll
  let initialized = false
  const html = doc.documentElement
  const noop = function () {}
  let checkTimer

  // visibility API strings
  let hiddenPropertyName = 'hidden'
  let visibilityChangeEventName = 'visibilitychange'

  // fallback to prefixed names in old webkit browsers
  if (doc.webkitHidden !== undefined) {
    hiddenPropertyName = 'webkitHidden'
    visibilityChangeEventName = 'webkitvisibilitychange'
  }

  // test getComputedStyle
  if (!win.getComputedStyle) {
    seppuku()
  }

  // test for native support
  const prefixes = ['', '-webkit-', '-moz-', '-ms-']
  const block = document.createElement('div')

  for (let i = prefixes.length - 1; i >= 0; i--) {
    try {
      block.style.position = prefixes[i] + 'sticky'
    } catch (e) {}
    if (block.style.position != '') {
      seppuku()
    }
  }

  updateScrollPos()

  // commit seppuku!
  function seppuku () {
    init = add = rebuild = pause = stop = kill = noop
  }

  function mergeObjects (targetObj, sourceObject) {
    for (const key in sourceObject) {
      if (sourceObject.hasOwnProperty(key)) {
        targetObj[key] = sourceObject[key]
      }
    }
  }

  function parseNumeric (val) {
    return parseFloat(val) || 0
  }

  function updateScrollPos () {
    scroll = {
      top: win.pageYOffset,
      left: win.pageXOffset
    }
  }

  function onScroll () {
    if (win.pageXOffset != scroll.left) {
      updateScrollPos()
      rebuild()
      return
    }

    if (win.pageYOffset != scroll.top) {
      updateScrollPos()
      recalcAllPos()
    }
  }

  // fixes flickering
  function onWheel (event) {
    setTimeout(function () {
      if (win.pageYOffset != scroll.top) {
        scroll.top = win.pageYOffset
        recalcAllPos()
      }
    }, 0)
  }

  function recalcAllPos () {
    for (let i = watchArray.length - 1; i >= 0; i--) {
      recalcElementPos(watchArray[i])
    }
  }

  function recalcElementPos (el) {
    if (!el.inited) return

    const currentMode = (scroll.top <= el.limit.start ? 0 : scroll.top >= el.limit.end ? 2 : 1)

    if (el.mode != currentMode) {
      switchElementMode(el, currentMode)
    }
  }

  // checks whether stickies start or stop positions have changed
  function fastCheck () {
    for (let i = watchArray.length - 1; i >= 0; i--) {
      if (!watchArray[i].inited) continue

      const deltaTop = Math.abs(getDocOffsetTop(watchArray[i].clone) - watchArray[i].docOffsetTop)
      const deltaHeight = Math.abs(watchArray[i].parent.node.offsetHeight - watchArray[i].parent.height)

      if (deltaTop >= 2 || deltaHeight >= 2) return false
    }
    return true
  }

  function initElement (el) {
    if (isNaN(parseFloat(el.computed.top)) || el.isCell || el.computed.display == 'none') return

    el.inited = true

    if (!el.clone) clone(el)
    if (el.parent.computed.position != 'absolute' &&
            el.parent.computed.position != 'relative') el.parent.node.style.position = 'relative'

    recalcElementPos(el)

    el.parent.height = el.parent.node.offsetHeight
    el.docOffsetTop = getDocOffsetTop(el.clone)
  }

  function deinitElement (el) {
    let deinitParent = true

    el.clone && killClone(el)
    mergeObjects(el.node.style, el.css)

    // check whether element's parent is used by other stickies
    for (let i = watchArray.length - 1; i >= 0; i--) {
      if (watchArray[i].node !== el.node && watchArray[i].parent.node === el.parent.node) {
        deinitParent = false
        break
      }
    };

    if (deinitParent) el.parent.node.style.position = el.parent.css.position
    el.mode = -1
  }

  function initAll () {
    for (let i = watchArray.length - 1; i >= 0; i--) {
      initElement(watchArray[i])
    }
  }

  function deinitAll () {
    for (let i = watchArray.length - 1; i >= 0; i--) {
      deinitElement(watchArray[i])
    }
  }

  function switchElementMode (el, mode) {
    const nodeStyle = el.node.style

    switch (mode) {
      case 0:
        nodeStyle.position = 'absolute'
        nodeStyle.left = el.offset.left + 'px'
        nodeStyle.right = el.offset.right + 'px'
        nodeStyle.top = el.offset.top + 'px'
        nodeStyle.bottom = 'auto'
        nodeStyle.width = 'auto'
        nodeStyle.marginLeft = 0
        nodeStyle.marginRight = 0
        nodeStyle.marginTop = 0
        break

      case 1:
        nodeStyle.position = 'fixed'
        nodeStyle.left = el.box.left + 'px'
        nodeStyle.right = el.box.right + 'px'
        nodeStyle.top = el.css.top
        nodeStyle.bottom = 'auto'
        nodeStyle.width = 'auto'
        nodeStyle.marginLeft = 0
        nodeStyle.marginRight = 0
        nodeStyle.marginTop = 0
        break

      case 2:
        nodeStyle.position = 'absolute'
        nodeStyle.left = el.offset.left + 'px'
        nodeStyle.right = el.offset.right + 'px'
        nodeStyle.top = 'auto'
        nodeStyle.bottom = 0
        nodeStyle.width = 'auto'
        nodeStyle.marginLeft = 0
        nodeStyle.marginRight = 0
        break
    }

    el.mode = mode
  }

  function clone (el) {
    el.clone = document.createElement('div')

    const refElement = el.node.nextSibling || el.node
    const cloneStyle = el.clone.style

    cloneStyle.height = el.height + 'px'
    cloneStyle.width = el.width + 'px'
    cloneStyle.marginTop = el.computed.marginTop
    cloneStyle.marginBottom = el.computed.marginBottom
    cloneStyle.marginLeft = el.computed.marginLeft
    cloneStyle.marginRight = el.computed.marginRight
    cloneStyle.padding = cloneStyle.border = cloneStyle.borderSpacing = 0
    cloneStyle.fontSize = '1em'
    cloneStyle.position = 'static'
    cloneStyle.cssFloat = el.computed.cssFloat

    el.node.parentNode.insertBefore(el.clone, refElement)
  }

  function killClone (el) {
    el.clone.parentNode.removeChild(el.clone)
    el.clone = undefined
  }

  function getElementParams (node) {
    const computedStyle = getComputedStyle(node)
    const parentNode = node.parentNode
    const parentComputedStyle = getComputedStyle(parentNode)
    const cachedPosition = node.style.position

    node.style.position = 'relative'

    const computed = {
      top: computedStyle.top,
      marginTop: computedStyle.marginTop,
      marginBottom: computedStyle.marginBottom,
      marginLeft: computedStyle.marginLeft,
      marginRight: computedStyle.marginRight,
      cssFloat: computedStyle.cssFloat,
      display: computedStyle.display
    }
    const numeric = {
      top: parseNumeric(computedStyle.top),
      marginBottom: parseNumeric(computedStyle.marginBottom),
      paddingLeft: parseNumeric(computedStyle.paddingLeft),
      paddingRight: parseNumeric(computedStyle.paddingRight),
      borderLeftWidth: parseNumeric(computedStyle.borderLeftWidth),
      borderRightWidth: parseNumeric(computedStyle.borderRightWidth)
    }

    node.style.position = cachedPosition

    const css = {
      position: node.style.position,
      top: node.style.top,
      bottom: node.style.bottom,
      left: node.style.left,
      right: node.style.right,
      width: node.style.width,
      marginTop: node.style.marginTop,
      marginLeft: node.style.marginLeft,
      marginRight: node.style.marginRight
    }
    const nodeOffset = getElementOffset(node)
    const parentOffset = getElementOffset(parentNode)

    const parent = {
      node: parentNode,
      css: {
        position: parentNode.style.position
      },
      computed: {
        position: parentComputedStyle.position
      },
      numeric: {
        borderLeftWidth: parseNumeric(parentComputedStyle.borderLeftWidth),
        borderRightWidth: parseNumeric(parentComputedStyle.borderRightWidth),
        borderTopWidth: parseNumeric(parentComputedStyle.borderTopWidth),
        borderBottomWidth: parseNumeric(parentComputedStyle.borderBottomWidth)
      }
    }

    const el = {
      node: node,
      box: {
        left: nodeOffset.win.left,
        right: html.clientWidth - nodeOffset.win.right
      },
      offset: {
        top: nodeOffset.win.top - parentOffset.win.top - parent.numeric.borderTopWidth,
        left: nodeOffset.win.left - parentOffset.win.left - parent.numeric.borderLeftWidth,
        right: -nodeOffset.win.right + parentOffset.win.right - parent.numeric.borderRightWidth
      },
      css: css,
      isCell: computedStyle.display == 'table-cell',
      computed: computed,
      numeric: numeric,
      width: nodeOffset.win.right - nodeOffset.win.left,
      height: nodeOffset.win.bottom - nodeOffset.win.top,
      mode: -1,
      inited: false,
      parent: parent,
      limit: {
        start: nodeOffset.doc.top - numeric.top,
        end: parentOffset.doc.top + parentNode.offsetHeight - parent.numeric.borderBottomWidth -
                        node.offsetHeight - numeric.top - numeric.marginBottom
      }
    }

    return el
  }

  function getDocOffsetTop (node) {
    let docOffsetTop = 0

    while (node) {
      docOffsetTop += node.offsetTop
      node = node.offsetParent
    }

    return docOffsetTop
  }

  function getElementOffset (node) {
    const box = node.getBoundingClientRect()

    return {
      doc: {
        top: box.top + win.pageYOffset,
        left: box.left + win.pageXOffset
      },
      win: box
    }
  }

  function startFastCheckTimer () {
    checkTimer = setInterval(function () {
      !fastCheck() && rebuild()
    }, 500)
  }

  function stopFastCheckTimer () {
    clearInterval(checkTimer)
  }

  function handlePageVisibilityChange () {
    if (!initialized) return

    if (document[hiddenPropertyName]) {
      stopFastCheckTimer()
    } else {
      startFastCheckTimer()
    }
  }

  function init () {
    if (initialized) return

    updateScrollPos()
    initAll()

    win.addEventListener('scroll', onScroll)
    win.addEventListener('wheel', onWheel)

    // watch for width changes
    win.addEventListener('resize', rebuild)
    win.addEventListener('orientationchange', rebuild)

    // watch for page visibility
    doc.addEventListener(visibilityChangeEventName, handlePageVisibilityChange)

    startFastCheckTimer()

    initialized = true
  }

  function rebuild () {
    if (!initialized) return

    deinitAll()

    for (let i = watchArray.length - 1; i >= 0; i--) {
      watchArray[i] = getElementParams(watchArray[i].node)
    }

    initAll()
  }

  function pause () {
    win.removeEventListener('scroll', onScroll)
    win.removeEventListener('wheel', onWheel)
    win.removeEventListener('resize', rebuild)
    win.removeEventListener('orientationchange', rebuild)
    doc.removeEventListener(visibilityChangeEventName, handlePageVisibilityChange)

    stopFastCheckTimer()

    initialized = false
  }

  function stop () {
    pause()
    deinitAll()
  }

  function kill () {
    stop()

    // empty the array without loosing the references,
    // the most performant method according to http://jsperf.com/empty-javascript-array
    while (watchArray.length) {
      watchArray.pop()
    }
  }

  function add (node) {
    // check if Stickyfill is already applied to the node
    for (let i = watchArray.length - 1; i >= 0; i--) {
      if (watchArray[i].node === node) return
    };

    const el = getElementParams(node)

    watchArray.push(el)

    if (!initialized) {
      init()
    } else {
      initElement(el)
    }
  }

  function remove (node) {
    for (let i = watchArray.length - 1; i >= 0; i--) {
      if (watchArray[i].node === node) {
        deinitElement(watchArray[i])
        watchArray.splice(i, 1)
      }
    };
  }

  // expose Stickyfill
  win.Stickyfill = {
    stickies: watchArray,
    add: add,
    remove: remove,
    init: init,
    rebuild: rebuild,
    pause: pause,
    stop: stop,
    kill: kill
  }
})(document, window)

// if jQuery is available -- create a plugin
if (window.jQuery) {
  (function ($) {
    $.fn.Stickyfill = function (options) {
      this.each(function () {
        Stickyfill.add(this)
      })

      return this
    }
  })(window.jQuery)
}

const stickyElements = document.getElementsByClassName('sticky')

for (let i = stickyElements.length - 1; i >= 0; i--) {
  Stickyfill.add(stickyElements[i])
}

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/from
// Production steps of ECMA-262, Edition 6, 22.1.2.1
if (!Array.from) {
  Array.from = (function () {
    const toStr = Object.prototype.toString
    const isCallable = function (fn) {
      return typeof fn === 'function' || toStr.call(fn) === '[object Function]'
    }
    const toInteger = function (value) {
      const number = Number(value)
      if (isNaN(number)) { return 0 }
      if (number === 0 || !isFinite(number)) { return number }
      return (number > 0 ? 1 : -1) * Math.floor(Math.abs(number))
    }
    const maxSafeInteger = Math.pow(2, 53) - 1
    const toLength = function (value) {
      const len = toInteger(value)
      return Math.min(Math.max(len, 0), maxSafeInteger)
    }

    // The length property of the from method is 1.
    return function from (arrayLike/*, mapFn, thisArg */) {
      // 1. Let C be the this value.
      const C = this

      // 2. Let items be ToObject(arrayLike).
      const items = Object(arrayLike)

      // 3. ReturnIfAbrupt(items).
      if (arrayLike == null) {
        throw new TypeError('Array.from requires an array-like object - not null or undefined')
      }

      // 4. If mapfn is undefined, then let mapping be false.
      const mapFn = arguments.length > 1 ? arguments[1] : void undefined
      let T
      if (typeof mapFn !== 'undefined') {
        // 5. else
        // 5. a If IsCallable(mapfn) is false, throw a TypeError exception.
        if (!isCallable(mapFn)) {
          throw new TypeError('Array.from: when provided, the second argument must be a function')
        }

        // 5. b. If thisArg was supplied, let T be thisArg; else let T be undefined.
        if (arguments.length > 2) {
          T = arguments[2]
        }
      }

      // 10. Let lenValue be Get(items, "length").
      // 11. Let len be ToLength(lenValue).
      const len = toLength(items.length)

      // 13. If IsConstructor(C) is true, then
      // 13. a. Let A be the result of calling the [[Construct]] internal method
      // of C with an argument list containing the single item len.
      // 14. a. Else, Let A be ArrayCreate(len).
      const A = isCallable(C) ? Object(new C(len)) : new Array(len)

      // 16. Let k be 0.
      let k = 0
      // 17. Repeat, while k < len… (also steps a - h)
      let kValue
      while (k < len) {
        kValue = items[k]
        if (mapFn) {
          A[k] = typeof T === 'undefined' ? mapFn(kValue, k) : mapFn.call(T, kValue, k)
        } else {
          A[k] = kValue
        }
        k += 1
      }
      // 18. Let putStatus be Put(A, "length", len, true).
      A.length = len
      // 20. Return A.
      return A
    }
  }())
}

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/includes#Polyfill
// https://tc39.github.io/ecma262/#sec-array.prototype.includes
if (!Array.prototype.includes) {
  Object.defineProperty(Array.prototype, 'includes', {
    value: function (searchElement, fromIndex) {
      // 1. Let O be ? ToObject(this value).
      if (this == null) {
        throw new TypeError('"this" is null or not defined')
      }

      const o = Object(this)

      // 2. Let len be ? ToLength(? Get(O, "length")).
      const len = o.length >>> 0

      // 3. If len is 0, return false.
      if (len === 0) {
        return false
      }

      // 4. Let n be ? ToInteger(fromIndex).
      //    (If fromIndex is undefined, this step produces the value 0.)
      const n = fromIndex | 0

      // 5. If n ≥ 0, then
      //  a. Let k be n.
      // 6. Else n < 0,
      //  a. Let k be len + n.
      //  b. If k < 0, let k be 0.
      let k = Math.max(n >= 0 ? n : len - Math.abs(n), 0)

      function sameValueZero (x, y) {
        return x === y || (typeof x === 'number' && typeof y === 'number' && isNaN(x) && isNaN(y))
      }

      // 7. Repeat, while k < len
      while (k < len) {
        // a. Let elementK be the result of ? Get(O, ! ToString(k)).
        // b. If SameValueZero(searchElement, elementK) is true, return true.
        // c. Increase k by 1.
        if (sameValueZero(o[k], searchElement)) {
          return true
        }
        k++
      }

      // 8. Return false
      return false
    }
  })
}
