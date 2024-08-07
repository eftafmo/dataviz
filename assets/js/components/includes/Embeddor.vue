<template>
  <div
    v-show="visible"
    class="embeddor"
    @mouseenter="popperEnter"
    @mouseleave="popperLeave"
  >
    <div class="x-container">
      <span class="icon icon-menu" @click="toggleExpanded"></span>
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

import WithFilters from "../mixins/WithFilters";
import { downloadFile } from "../../lib/util";

export default {
  mixins: [WithFilters],
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
    offsetY: {
      type: Number,
      required: false,
      default: 10,
    },
    offsetX: {
      type: Number,
      required: false,
      default: -25,
    },
  },
  data() {
    return {
      padding: 10,
      target: null,
      timeout: 400,
      scenario: "none",

      target_hovered: false,
      popper_hovered: false,

      expanded: false,
      copied: false,
      // See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas#maximum_canvas_size
      // Don't push this to the limit, set something more sensible here.
      maxCanvasSize: 1280,
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

      Object.entries(this.filters).forEach(([k, v]) => {
        if (v) url.searchParams.append(k, v);
      });
      return url.toString();
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
          placement: "right-start",

          modifiers: {
            offset: {
              offset: `${this.offsetY}px,${this.offsetX}px`,
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
      () => (this.target_hovered = true),
    );
    this.target.addEventListener(
      "mouseleave",
      () => (this.target_hovered = false),
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
      width = Math.min(width * this.scaleDownload, this.maxCanvasSize);
      height = Math.min(height * this.scaleDownload, this.maxCanvasSize);

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

      const filename = `${this.period}-${this.scenario}-${this.tag}.png`;

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

        canvas.toBlob((blob) => downloadFile(blob, filename), "image/png");
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
  z-index: 2;

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
    right: 0;
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
