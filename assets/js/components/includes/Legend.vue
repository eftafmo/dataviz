<template>
<div class="legend" :class="{ 'no-total': !what }">
  <p class="what" v-if="what">{{ total }} {{ what }}</p>

  <ul :class="{active: clickFunc}">
    <li
        v-for="item in items"
        @click="clickFunc && clickFunc(item, $event.target)"
        :class="{
                  selected: item.selected,
                  disabled: item.disabled,
                  zero: item.value == 0,
                }"
    >
      <slot name="item" :item="item">
        <span class="fill" :style="{backgroundColor: item.colour}"></span>
        {{ item.name }}
        <sup v-if="showValues && item.value !== undefined" class="value">{{ formatFunc(item.value) }}</sup>
      </slot>
    </li>
  </ul>
</div>
</template>


<style lang="less">
.viz .legend {
  margin-bottom: .5em;

  ul {
    li {
      list-style-type: none;
      margin-bottom: .2em;

      &.disabled, &.zero {
        filter: grayscale(100%);
        opacity: 0.5;
      }

      &.selected {
        text-shadow: 0 0 1px #999;
      }

      transition: all .5s ease;

      span.fill {
        display: inline-block;
        vertical-align: text-bottom;
        width: 1.2em;
        height: 1.2em;
        margin-right: 0.2em;
      }

      sup.value {
        font-weight: bold;
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

    p.what, ul li {
      display: inline-block;
      margin-right: 1.5em;
      margin-bottom: 0;
    }
  }
}
</style>


<script>
import Vue from 'vue';


export default Vue.extend({
  props: {
    items: {
      type: Array,
      required: true,
    },

    clickFunc: {
      // if provided, the legend is clickable
      type: Function,
    },

    formatFunc: {
      type: Function,
      default: x => x,
    },

    showValues: {
      type: Boolean,
      default: true,
    },

    what: {
      // what this legend deals with.
      // considered a confirmation to show the things count.
      type: String,
    },
  },

  computed: {
    total() {
      return this.items.reduce( (x, item) => x + item.value, 0)
    },
  },
});
</script>
