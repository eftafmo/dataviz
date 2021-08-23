<template>
  <div
    v-show="visible"
    class="embeddor"
    @mouseenter="popperEnter"
    @mouseleave="popperLeave"
  >
    <div class="x-container">
      <span class="icon icon-embed" @click="toggleExpanded"></span>
      <div v-show="expanded" class="content">
        <template v-if="svgNode">
          <p class="title">Download</p>
          <p>
            <button @click="downloadChart">Download chart as .png</button>
          </p>
          <hr />
        </template>
        <p class="title">Embed</p>
        <p>
          <small>
            Paste the following into your markup where you want the embedded
            component to appear
          </small>
        </p>
        <p>
          <input ref="txt" type="text" :value="code" readonly />
          <button ref="btn">copy</button>
        </p>
        <div v-show="copied" class="ok">copied</div>
      </div>
    </div>
  </div>
</template>

<script>
import { default as Popper } from "popper.js";
import { default as Clipboard } from "clipboard";

import { FILTERS } from "../mixins/WithFilters";
import { downloadFile } from "../../lib/util";

export default {
  props: {
    tag: {
      type: String,
      required: true,
    },
    period: {
      type: String,
      required: true,
    },
    svgNode: {
      type: Element,
      required: false,
      default: null,
    },
    scaleDownload: {
      type: Number,
      required: false,
      default: 1,
    },
  },
  data() {
    return {
      padding: 10,
      target: null,
      timeout: 400,

      target_hovered: false,
      popper_hovered: false,

      expanded: false,
      copied: false,
    };
  },
  computed: {
    isEmbedded() {
      return !!this.$.root.props.embedded;
    },
    visible() {
      return !this.isEmbedded && (this.target_hovered || this.popper_hovered);
    },
    path() {
      return `/embed/${this.period}/${this.scenario}/${this.tag}.js`;
    },
    url() {
      const url = new URL(this.path, window.location.href);

      for (const f in FILTERS) {
        const v = FILTERS[f];
        if (v === null) continue;

        url.searchParams.set(f, v);
      }

      return url.href;
    },
    code() {
      if (this.target === null) return "";
      return `<script src="${this.url}" async><` + `/script>`;
    },
  },
  watch: {
    visible() {
      this.expanded = false; // start clean

      if (!this.visible) this._popper.destroy();
      else
        this._popper = new Popper(this.target, this.$el, {
          placement: "left-start",

          modifiers: {
            offset: {
              offset: "0px,0px",
            },

            preventOverflow: { enabled: false },
            flip: { enabled: false },
            hide: { enabled: false },
          },
        });
    },
    // focus on expand, maybe?
    expanded(v) {
      if (v)
        this.$nextTick(() => {
          this.$refs.txt.select();
          this.$refs.txt.focus();
        });
    },
  },
  mounted() {
    if (this.isEmbedded) return;

    this.scenario = this.$root.$options.name.toLowerCase();
    this.target = this.$el.parentElement;
    this.target.addEventListener(
      "mouseenter",
      () => (this.target_hovered = true)
    );
    this.target.addEventListener(
      "mouseleave",
      () => (this.target_hovered = false)
    );

    const clipboard = new Clipboard(this.$refs.btn, {
      target: () => this.$refs.txt,
    });

    let _donecopy;
    clipboard.on("success", (e) => {
      e.clearSelection();

      clearTimeout(_donecopy);
      this.copied = true;

      _donecopy = setTimeout(() => (this.copied = false), this.timeout);
    });
    clipboard.on("error", (e) => {
      console.error(e);
    });
  },

  methods: {
    downloadChart() {
      // XXX Apple is being a dingus as usual.
      const URL = window.URL || window.webkitURL || window;

      const svgStyle = window.getComputedStyle(this.svgNode);
      let { width, height } = this.svgNode.getBBox();
      width *= this.scaleDownload;
      height *= this.scaleDownload;

      // Clone the node and make several required adjustments
      const clonedSVGNode = this.svgNode.cloneNode(true);
      // Must set width and height. See Firefox bug:
      // https://bugzilla.mozilla.org/show_bug.cgi?id=700533
      clonedSVGNode.setAttribute("width", width);
      clonedSVGNode.setAttribute("height", height);
      // Ensure the xmlns is set, otherwise it cannot be drawn
      clonedSVGNode.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      // Ensure we use the same font when drawing the image into the canvas.
      // CSS styles don't cascade into image drawn into the canvas.
      clonedSVGNode.setAttribute("font-family", svgStyle.fontFamily);

      const outerHTML = clonedSVGNode.outerHTML.replaceAll("&nbsp;", "&#160;");
      const blob = new Blob([outerHTML], {
        type: "image/svg+xml;charset=utf-8",
      });

      // XXX Use to debug SVG issues. The browser WILL not show any details
      // XXX about errors while drawing the SVG into the canvas.
      // return downloadFile(blob, "test.svg");

      const blobURL = URL.createObjectURL(blob);
      const img = new Image();
      img.crossOrigin = "Anonymous";
      // TODO: let the user know that this failed? Or maybe log to Sentry?
      img.onerror = console.log;
      img.onload = () => {
        URL.revokeObjectURL(blobURL);

        const canvas = document.createElement("canvas");

        canvas.width = width + this.padding * 2;
        canvas.height = height + this.padding * 2;
        const context = canvas.getContext("2d");

        context.fillStyle = "white";
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, this.padding, this.padding, width, height);

        canvas.toBlob((blob) => {
          downloadFile(blob, `${this.period}-${this.scenario}-${this.tag}.png`);
        }, "image/png");
      };
      img.src = blobURL;
    },
    popperEnter() {
      clearTimeout(this._pleaving);
      this.popper_hovered = true;
    },
    popperLeave() {
      this._pleaving = setTimeout(() => {
        this.popper_hovered = false;
        this.expanded = false;
      }, this.timeout);
    },
    toggleExpanded() {
      this.expanded = !this.expanded;
    },
  },
};
</script>

<style lang="less">
.embeddor {
  // make sure it never affects page layout
  @media (max-width: 768px) {
    display: none;
  }
  position: absolute;
  right: 0;
  bottom: 0;

  width: 1em;
  height: 1em;
  z-index: 999;

  .x-container {
    position: relative;
  }

  .icon {
    cursor: pointer;
    font-weight: bold;
    font-size: 1.5rem;
  }

  .content {
    position: absolute;
    background: white;
    border: 1px solid black;
    padding: 5px;

    .title {
      font-weight: bold;
      font-size: 16px;
      margin: 0;
    }
  }

  .ok {
    position: absolute;
    right: 10px;
    bottom: 10px;
    padding: 2px 3px;
    background: rgba(0, 0, 0, 0.7);
    color: #fff;
    border: 1px solid black;
  }
}
</style>
