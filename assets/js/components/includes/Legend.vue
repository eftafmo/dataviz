<template>
  <div class="chart-legend" :class="{ 'no-total': !what }">
    <p v-if="what" class="what">{{ total }} {{ what }}</p>

    <ul :class="{ active: clickFunc }">
      <li
        v-for="item in items"
        :key="item.id"
        :class="{
          selected: item.selected,
          disabled: item.disabled,
          zero: item.value === 0,
        }"
        @click="clickFunc && clickFunc(item, $event.target)"
      >
        <slot name="item" :item="item">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 10 10"
            class="fill"
          >
            <rect
              width="10"
              height="10"
              :fill="item.stripesFill || item.colour"
            ></rect>
          </svg>
          {{ item.name }}
          <sup v-if="showValues && item.value !== undefined" class="value">
            {{ format(item.value) }}
          </sup>
        </slot>
      </li>
    </ul>
  </div>
</template>

<script>
import ComponentMixin from "../mixins/Component.js";

export default {
  mixins: [ComponentMixin],

  props: {
    items: {
      type: Array,
      required: true,
    },

    clickFunc: {
      // if provided, the legend is clickable
      type: Function,
      default: null,
    },

    formatFunc: {
      type: Function,
      default: null,
    },

    showValues: {
      type: Boolean,
      default: true,
    },

    what: {
      // what this legend deals with.
      // considered a confirmation to show the things count.
      type: String,
      default: null,
    },
  },

  computed: {
    total() {
      return this.items.reduce((x, item) => x + item.value, 0);
    },
  },

  methods: {
    format(v) {
      return this.formatFunc ? this.formatFunc(v) : this.number(v);
    },
  },
};
</script>

<style lang="less">
.dataviz .viz .chart-legend {
  margin-bottom: 0.5em;

  ul {
    li {
      list-style-type: none;
      margin-bottom: 0.2em;

      &.disabled,
      &.zero {
        filter: grayscale(100%);
        opacity: 0.5;
      }

      transition: all 0.5s ease;

      .fill {
        display: inline-block;
        vertical-align: text-bottom;
        width: 1.2em;
        height: 1.2em;
        margin-right: 0.2em;
      }

      sup.value {
        font-weight: bold;
        color: #868686;
      }
    }

    &.active {
      li {
        cursor: pointer;
        &.zero {
          cursor: not-allowed;
        }
      }
    }
  }

  &.inline {
    &.no-total {
      padding-left: 2em;
    }

    ul {
      display: inline-block;
      padding: 0;
    }

    p.what,
    ul li {
      display: inline-block;
      margin-right: 1.5em;
      margin-bottom: 0;
    }
  }
}
</style>
