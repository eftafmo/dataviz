function _getmethod(spec, m) {
  if (spec.methods) return spec.methods[m]
}

function discover(spec, m) {
  let method

  const mixins = spec.mixins,
        ancestor = spec.extends

  if (mixins) for (const mixin of mixins) {
    method = _getmethod(mixin, m)

    if (method !== undefined)
      return method
  }

  // TODO: maybe don't return above and wrap both mixin and parent (extends)
  // methods in a single function? (multiple inheritance? do it for all mixins?)

  if (ancestor) {
    method = _getmethod(ancestor, m)

    if (method !== undefined)
      return method

    return discover(ancestor, m)
  }
}

export default function $super () {
  let _super = this.$.$_super
  if (_super !== undefined) return _super

  _super = this.$.$_super = new Proxy(this, {
    get(target, prop, receiver) {
      const func = discover(target.$options, prop)
      // TODO: cache me!
      if (func) {
        const bound = func.bind(target)

        return bound
      }
    },
  })

  return _super
}
