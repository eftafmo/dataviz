// TODO: this is very bad. it messes with embeds.
// should be a component or in a different js bundle.
window.Header = (function() {

  var el = document.querySelector('.dataviz .header');
  if (!el) return;

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

  var menus = el.querySelector('.header-inner')

  var active;

  function _bodyClass(targetName) {
    return targetName + '-is-open';
  }

  var open = function(targetName) {
    var target = menus;

    close();

    active = targetName;
    document.body.classList.add(_bodyClass(targetName));

    target.classList.add('is-open');
    backdrop.show();
    //target.querySelector('input').focus();
  };

  var close = function() {
    if (active) {
      var target = menus;
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
