import 'url-polyfill';

if (!Object.assign) {
  Object.defineProperty(Object, 'assign', {
    enumerable: false,
    configurable: true,
    writable: true,
    value: function(target) {
      'use strict';
      if (target === undefined || target === null) {
        throw new TypeError('Cannot convert first argument to object');
      }

      var to = Object(target);
      for (var i = 1; i < arguments.length; i++) {
        var nextSource = arguments[i];
        if (nextSource === undefined || nextSource === null) {
          continue;
        }
        nextSource = Object(nextSource);

        var keysArray = Object.keys(Object(nextSource));
        for (var nextIndex = 0, len = keysArray.length; nextIndex < len; nextIndex++) {
          var nextKey = keysArray[nextIndex];
          var desc = Object.getOwnPropertyDescriptor(nextSource, nextKey);
          if (desc !== undefined && desc.enumerable) {
            to[nextKey] = nextSource[nextKey];
          }
        }
      }
      return to;
    }
  });
}

/*
  the following functions are courtesy of MDN, released in the public domain.
  https://developer.mozilla.org/en-US/docs/MDN/About#Copyrights_and_licenses
*/
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/find
if (!Array.prototype.find) {
  Object.defineProperty(Array.prototype, 'find', {
    value: function(predicate) {
     // 1. Let O be ? ToObject(this value).
      if (this == null) {
        throw new TypeError('"this" is null or not defined');
      }

      var o = Object(this);

      // 2. Let len be ? ToLength(? Get(O, "length")).
      var len = o.length >>> 0;

      // 3. If IsCallable(predicate) is false, throw a TypeError exception.
      if (typeof predicate !== 'function') {
        throw new TypeError('predicate must be a function');
      }

      // 4. If thisArg was supplied, let T be thisArg; else let T be undefined.
      var thisArg = arguments[1];

      // 5. Let k be 0.
      var k = 0;

      // 6. Repeat, while k < len
      while (k < len) {
        // a. Let Pk be ! ToString(k).
        // b. Let kValue be ? Get(O, Pk).
        // c. Let testResult be ToBoolean(? Call(predicate, T, « kValue, k, O »)).
        // d. If testResult is true, return kValue.
        var kValue = o[k];
        if (predicate.call(thisArg, kValue, k, o)) {
          return kValue;
        }
        // e. Increase k by 1.
        k++;
      }

      // 7. Return undefined.
      return undefined;
    }
  });
}

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/fill
if (!Array.prototype.fill) {
  Object.defineProperty(Array.prototype, 'fill', {
    value: function(value) {

      // Steps 1-2.
      if (this == null) {
        throw new TypeError('this is null or not defined');
      }

      var O = Object(this);

      // Steps 3-5.
      var len = O.length >>> 0;

      // Steps 6-7.
      var start = arguments[1];
      var relativeStart = start >> 0;

      // Step 8.
      var k = relativeStart < 0 ?
        Math.max(len + relativeStart, 0) :
        Math.min(relativeStart, len);

      // Steps 9-10.
      var end = arguments[2];
      var relativeEnd = end === undefined ?
        len : end >> 0;

      // Step 11.
      var final = relativeEnd < 0 ?
        Math.max(len + relativeEnd, 0) :
        Math.min(relativeEnd, len);

      // Step 12.
      while (k < final) {
        O[k] = value;
        k++;
      }

      // Step 13.
      return O;
    }
  });
}

// https://developer.mozilla.org/en-US/docs/Web/API/ChildNode/remove
// from:https://github.com/jserz/js_piece/blob/master/DOM/ChildNode/remove()/remove().md
(function (arr) {
  arr.forEach(function (item) {
    if (item.hasOwnProperty('remove')) {
      return;
    }
    Object.defineProperty(item, 'remove', {
      configurable: true,
      enumerable: true,
      writable: true,
      value: function remove() {
        this.parentNode.removeChild(this);
      }
    });
  });
})([Element.prototype, CharacterData.prototype, DocumentType.prototype]);



// https://tc39.github.io/ecma262/#sec-array.prototype.findIndex
if (!Array.prototype.findIndex) {
  Object.defineProperty(Array.prototype, 'findIndex', {
    value: function(predicate) {
     // 1. Let O be ? ToObject(this value).
      if (this == null) {
        throw new TypeError('"this" is null or not defined');
      }

      var o = Object(this);

      // 2. Let len be ? ToLength(? Get(O, "length")).
      var len = o.length >>> 0;

      // 3. If IsCallable(predicate) is false, throw a TypeError exception.
      if (typeof predicate !== 'function') {
        throw new TypeError('predicate must be a function');
      }

      // 4. If thisArg was supplied, let T be thisArg; else let T be undefined.
      var thisArg = arguments[1];

      // 5. Let k be 0.
      var k = 0;

      // 6. Repeat, while k < len
      while (k < len) {
        // a. Let Pk be ! ToString(k).
        // b. Let kValue be ? Get(O, Pk).
        // c. Let testResult be ToBoolean(? Call(predicate, T, « kValue, k, O »)).
        // d. If testResult is true, return k.
        var kValue = o[k];
        if (predicate.call(thisArg, kValue, k, o)) {
          return k;
        }
        // e. Increase k by 1.
        k++;
      }

      // 7. Return -1.
      return -1;
    }
  });
}

/*!
  sticky-position 1.0.1
  license: MIT
  http://www.jacklmoore.com/sticky-position
*/
(function (global, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'module'], factory);
  } else if (typeof exports !== 'undefined' && typeof module !== 'undefined') {
    factory(exports, module);
  } else {
    var mod = {
      exports: {}
    };
    factory(mod.exports, mod);
    global.stickyPosition = mod.exports;
  }
})(this, function (exports, module) {
  'use strict';

  module.exports = function () {
    var _ref = arguments[0] === undefined ? {} : arguments[0];

    var _ref$primary = _ref.primary;
    var primary = _ref$primary === undefined ? null : _ref$primary;
    var _ref$placeholder = _ref.placeholder;
    var placeholder = _ref$placeholder === undefined ? null : _ref$placeholder;
    var _ref$wrapper = _ref.wrapper;
    var wrapper = _ref$wrapper === undefined ? null : _ref$wrapper;
    var _ref$computeWidth = _ref.computeWidth;
    var computeWidth = _ref$computeWidth === undefined ? true : _ref$computeWidth;

    var top = null;
    var isSticky = false;

    var nativeSupport = (function () {
      if (this.isSupported !== null) {
        return this.isSupported;
      } else {
        var style = document.createElement('test').style;
        style.cssText = ['-webkit-', '-ms-', ''].map(function (prefix) {
          return 'position: ' + prefix + 'sticky';
        }).join(';');
        this.isSupported = style.position.indexOf('sticky') !== -1;
        return this.isSupported;
      }
    }).bind({ isSupported: null });

    function stick() {
      if (isSticky === true) return;
      primary.style.position = 'fixed';
      isSticky = true;
    }

    function unstick() {
      if (isSticky === false) return;
      primary.style.position = 'relative';
      primary.style.width = '';
      primary.style.top = '';
      primary.style.left = '';
      placeholder.style.height = '';
      placeholder.style.width = '';
      isSticky = false;
    }

    function init() {
      var supportsPassive = false;
      try {
        var opts = Object.defineProperty({}, 'passive', {
          get: function get() {
            supportsPassive = true;
          }
        });
        window.addEventListener('test', null, opts);
      } catch (e) {}

      // positioning necessary for getComputedStyle to report the correct z-index value.
      wrapper.style.position = 'relative';

      var style = window.getComputedStyle(wrapper, null);

      top = parseInt(style.top) || 0;
      primary.style.zIndex = style.zIndex;
      primary.style.position = 'relative';
      wrapper.style.top = 0;
      // Giving the placeholder an overflow of 'hidden' or 'auto' will allow it to clear any bottom margin extending beneath the primary element.
      // Clearing that margin is needed so that it's contribution to the wrapper element's height can be measured with getBoundingClientRect.
      placeholder.style.overflow = 'hidden';

      update();
      window.addEventListener('load', update);
      window.addEventListener('scroll', update, supportsPassive ? { passive: true } : false);
      window.addEventListener('resize', update);
    }

    function update() {
      var rect = wrapper.getBoundingClientRect();
      var sticky = rect.top < top;

      if (sticky) {
        placeholder.style.height = rect.height + 'px';

        if (computeWidth) {
          placeholder.style.width = rect.width + 'px';
        }

        var parentRect = wrapper.parentNode.getBoundingClientRect();

        primary.style.top = Math.min(parentRect.top + parentRect.height - rect.height, top) + 'px';
        primary.style.width = computeWidth ? rect.width + 'px' : '100%';
        primary.style.left = rect.left + 'px';

        stick();
      } else {
        unstick();
      }
    }

    function destroy() {
      window.removeEventListener('load', update);
      window.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
      unstick();
    }

    if (nativeSupport()) {
      return {
        update: function update() {},
        destroy: function destroy() {}
      };
    } else {
      init();

      return {
        update: update,
        destroy: destroy };
    }
  };
});
