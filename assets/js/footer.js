import axios from "axios";

window.Footer = (function () {
  var elFromMarkup = function (markup, selector) {
    var content = document.createElement("div");
    content.innerHTML = markup;
    return content.querySelector(selector);
  };

  var Backdrop = function (el, onHide) {
    let hide = function () {
      onHide ? onHide() : null;
      el.style.zIndex = "";
      el.style.display = "";
      el.removeEventListener("click", hide, false);
    };

    let show = function () {
      el.style.display = "block";
      el.style.zIndex = "200";
      el.addEventListener("click", hide, false);
    };

    return {
      show: show,
      hide: hide,
    };
  };

  var Popup = function (target, content) {
    let elBackdrop = document.querySelector("#backdrop");
    let el = document.createElement("div");

    el.className = "modal-popup";
    el.innerHTML = `
      <button type="button" title="Close popup" class="no-btn close-btn">
        <span class="icon icon-cross"></span>
      </button>
      <div class="content">${content.innerHTML}</div>
    `;

    let backdrop;

    let hideOnEsc = function (e) {
      if (e.keyCode === 27) {
        backdrop.hide();
        window.removeEventListener("keyup", hideOnEsc, false);
      }
    };

    var show = function () {
      let modal = target.appendChild(el);
      backdrop = Backdrop(
        elBackdrop,
        function () {
          this.hide(target, modal);
        }.bind(this)
      );

      target.style.overflow = "hidden";

      backdrop.show();

      el.querySelector("button").addEventListener("click", backdrop.hide);

      window.addEventListener("keyup", hideOnEsc, false);
    };

    var hide = function (target, modal) {
      target.removeChild(modal);
      target.style.overflow = "initial";
    };

    return {
      show: show,
      hide: hide,
    };
  };

  var popup = function (evt, el) {
    evt.preventDefault();

    axios.get(el.href).then((resp) => {
      let content = elFromMarkup(resp.data, "#content .main");
      Popup(document.body, content).show();
    });

    return false;
  };

  return {
    popup: popup,
  };
})();
