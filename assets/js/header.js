// TODO: this is very bad. it messes with embeds.
// should be a component or in a different js bundle.
window.Header = (function() {

  var el = document.querySelector('.header');
  if (!el) return; // TODO: at least make this selector more specific

  var backdrop = function() {
    var el = document.createElement('DIV');
    el.id = 'backdrop';
    document.body.appendChild(el);

    return {
      el: el,
      show: function() { el.style.display = 'block'; },
      hide: function() { el.style.display = 'none'; }
    }
  }();

  var menus = {
    'search': el.querySelector('.header-search'),
    'menu': el.querySelector('.header-menu')
  };

  var active;

  function _bodyClass(targetName) {
    return targetName + '-is-open';
  }

  var open = function(targetName) {
    var target = menus[targetName];

    close();

    active = targetName;
    document.body.classList.add(_bodyClass(targetName));

    target.classList.add('is-open');
    backdrop.show();

    if (targetName === 'search')
      target.querySelector('input').focus();
  };

  var close = function() {
    if (active) {
      var target = menus[active];
      
      document.body.classList.remove(_bodyClass(active));
      target.classList.remove('is-open');

      active = undefined;
      backdrop.hide();
    }
  };

  backdrop.el.addEventListener('click', close, false);

  window.addEventListener('keyup', function(e) {
    if (e.keyCode === 27 && active)
      close()
  });

  return {
    open: open,
    close: close,
    toggle: function(targetName) {
      if (active != targetName) {
        open(targetName)
      } else {
        close()
      }
    }
  }
}());
