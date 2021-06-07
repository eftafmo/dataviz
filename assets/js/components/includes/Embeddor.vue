<template>
<div class="embeddor"
     v-show="visible"
     @mouseenter="popperEnter"
     @mouseleave="popperLeave"
>
  <div class="x-container">
    <span class="icon icon-embed" @click="toggleExpanded"></span>
    <div class="content" v-show="expanded">
      <p><small>Paste the following into your markup where you want the embedded component to appear</small></p>
      <p>
        <input type="text" :value="code" readonly ref="txt">
        <button ref="btn">copy</button>
      </p>
      <div class="ok" v-show="copied">copied</div>
    </div>
  </div>
</div>
</template>


<style lang="less">
.embeddor {
  // make sure it never affects page layout
  @media(max-width: 768px){
    display: none;
  }
  position: absolute;
  right: 0; bottom: 0;

  width: 1em;
  height: 1em;

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
    background: rgba(255, 255, 255, .7);
    border: 1px solid black;
    padding: 5px;
  }

  .ok {
    position: absolute;
    right: 10px;
    bottom: 10px;
    padding: 2px 3px;
    background: rgba(0, 0, 0, .7);
    color: #fff;
    border: 1px solid black;
  }
}
</style>


<script>
import {default as Popper} from 'popper.js'
import {default as Clipboard} from 'clipboard'

import {FILTERS} from '../mixins/WithFilters'


export default {
  props: {
    // all target components
    components: {
      type: Array,
    }
  },

  data() {
    return {
      // targets collection
      targets: null,
      // current target
      target: null,

      timeout: 400,

      target_hovered: false,
      popper_hovered: false,

      expanded: false,
      copied: false,
    }
  },

  computed: {
    visible() {
      return this.target_hovered || this.popper_hovered
    },

    path() {
      return `/embed/${ this.scenario }/${ this.target.tag }.js`
    },

    url() {
      const url = new URL(this.path, window.location.href)

      for (const f in FILTERS) {
        const v = FILTERS[f]
        if (v === null) continue

        url.searchParams.set(f, v)
      }

      return url.href.substr(url.protocol.length)
    },

    code() {
      if (this.target === null) return ""
      return '<' + 'script' +
             ` src="${ this.url }"` +
             ' async></' + 'script>'
    },
  },

  created() {
    // !!! TODO: FIXME !!! //
    return

    // cache the current scenario name
    this.scenario = this.$root.$options.name.toLowerCase()

    // set up the target properties and event handlers
    // when the component list is received
    // (and make sure the watcher is destroyed afterwards)
    const _unwatch = this.$watch("components", components => {
      // we need to delay this, or we won't have access to the unwatcher
      setTimeout(() => {
        if(components.length) {
          this.registerTargets()
          _unwatch()
        }
      })
    }, { immediate: true })
  },

  mounted() {
    const clipboard = new Clipboard(this.$refs.btn, {
      target: () => this.$refs.txt,
    })

    let _donecopy
    clipboard.on('success', (e) => {
      e.clearSelection()

      clearTimeout(_donecopy)
      this.copied = true

      _donecopy = setTimeout(
        () => this.copied = false,
        this.timeout
      )
    })
    clipboard.on('error', (e) => {
      console.error(e)
    })
  },

  methods: {
    getEmbedElementTarget(component) {
      // what element should we adorn with the embed code?
      let el

      // let's hardcode here all the logic, since it's well-defined
      // and's never gonna change

      if (component.$parent == this.$root) {
        // we could target the first h-something, but no need to,
        // this will always be an h2... right?
        el = component.$el.querySelector("h2")
      }
      else if (component.$parent.$el.getAttribute("role") == "tabpanel") {
        // let's look for the tab thingie
        el = component.$parent.$parent.$el.querySelector(
          `[role="tab"][aria-controls="${component.$parent.hash}"]`
        )
      }

      // else (sidebar summary), or if not found (homepage), fallback
      if (!el) el = component.$el

      return el
    },

    registerTargets() {
      const targets = {}

      for (const component of this.components) {
        const tag = component.$vnode.componentOptions.tag
        // components can override their embed button target
        const el = component.getEmbedElementTarget ?
                   component.getEmbedElementTarget() :
                   this.getEmbedElementTarget(component)

        // we should probably not use private stuff, but oh well
        const id = component._uid

        targets[id] = {
          tag: tag,
          el: el,
        }

        el.addEventListener("mouseenter", this.mkMouseEnter(id))
        el.addEventListener("mouseleave", this.mkMouseLeave(id))
      }

      this.targets = targets
    },

    mkMouseEnter(tid) {
      return () => {
        clearTimeout(this._tleaving)

        this.target = this.targets[tid] // <-- the magical trigger
        this.target_hovered = true
      }
    },

    mkMouseLeave(tid) {
      return () => {
        this._tleaving = setTimeout(
          () => this.target_hovered = false,
          this.timeout
        )
      }
    },

    popperEnter() {
      clearTimeout(this._pleaving)

      this.popper_hovered = true
    },

    popperLeave() {
      this._pleaving = setTimeout(
        () => this.popper_hovered = false,
        this.timeout
      )
    },

    toggleExpanded() {
      this.expanded = !this.expanded
    },
  },

  watch: {
    target(curr, prev) {
      this.expanded = false // start clean

      if (curr === null) this._popper.destroy()

      else this._popper = new Popper(
        curr.el, this.$el, {
          placement: "left-start",

          modifiers: {
            offset: {
              offset: "0px,0px",
            },

            preventOverflow: { enabled: false },
            flip: { enabled: false },
            hide: { enabled: false },
          },
        }
      )
    },

    visible(v) {
      // cleanup on hide
      if (!v) this.target = null
    },

    // focus on expand, maybe?
    expanded(v) {
      if(v) this.$nextTick(() => {
        this.$refs.txt.select()
        this.$refs.txt.focus()
      })
    },
  },
}
</script>
