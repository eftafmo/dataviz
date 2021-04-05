import * as d3 from 'd3'
import FMS from 'js/constants/financial-mechanisms.json5'
import FMLegendComponent from '../includes/FMLegend'

export function fmcolour (fmid) {
  return FMS[fmid].colour
}

export default {
  beforeCreate () {
    this.FMS = FMS
  },

  components: {
    'fm-legend': FMLegendComponent
  },

  computed: {
    // TODO: make the constants arrays, and the objects pre-computed
    FM_ARRAY () {
      return d3.values(this.FMS)
    }
  },

  methods: {
    fmcolour,

    getFilterClassFm (fm) {
      if (!this.filters.fm) { return }

      if (this.isSelectedFm(fm)) { return 'selected' }

      if (this.isDisabledFm(fm)) { return 'disabled' }
    },

    isSelectedFm (fm) {
      if (!this.filters.fm) return
      return this.filters.fm === fm.name
    },
    isDisabledFm (fm) {
      if (!this.filters.fm) return
      return this.filters.fm !== fm.name
    },

    toggleFm (fm, etarget) {
      // don't filter by zero-valued items
      if (fm.value === 0) return

      const fmname = fm.name
      this.filters.fm = this.filters.fm === fmname
        ? null
        : fmname
    }
  }
}
