// TODO: this is very bad. it messes with embeds.
// should be a component or in a different js bundle.
window.Header = (function () {
  const el = document.querySelector('.dataviz .header')
  if (!el) return

  const backdrop = (function () {
    const el = document.createElement('DIV')
    el.id = 'backdrop'
    document.body.appendChild(el)

    return {
      el: el,
      show: function () { el.style.display = 'block' },
      hide: function () { el.style.display = 'none' }
    }
  }())

  const menus = el.querySelector('.header-inner')

  let active

  function _bodyClass (targetName) {
    return targetName + '-is-open'
  }

  const open = function (targetName) {
    const target = menus

    close()

    active = targetName
    document.body.classList.add(_bodyClass(targetName))

    target.classList.add('is-open')
    backdrop.show()
    // target.querySelector('input').focus();
  }

  const close = function () {
    if (active) {
      const target = menus
      document.body.classList.remove(_bodyClass(active))
      target.classList.remove('is-open')

      active = undefined
      backdrop.hide()
    }
  }

  backdrop.el.addEventListener('click', close, false)

  window.addEventListener('keyup', function (e) {
    if (e.code === 'Escape' && active) { close() }
  })

  return {
    open: open,
    close: close,
    toggle: function (targetName) {
      if (active !== targetName) {
        open(targetName)
      } else {
        close()
      }
    }
  }
}())
