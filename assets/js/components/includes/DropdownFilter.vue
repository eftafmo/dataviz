<template>
  <select class="viz-select clearfix" :style="{ width }" @change="setFilter">
    <option value="">
      {{ title }}
    </option>
    <option
      v-for="item in items"
      :key="getFilterName(item)"
      :value="getFilterName(item)"
      :selected="getFilterName(item) === current"
    >
      {{ getFilterDisplayName(item) }}
    </option>
  </select>
</template>

<script>
import WithFiltersMixin from "../mixins/WithFilters";

export default {
  mixins: [WithFiltersMixin],

  props: {
    items: {
      type: Object,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    filter: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      width: "auto",
    };
  },
  computed: {
    current() {
      return this.filters[this.filter];
    },
    currentItem() {
      return this.items.find(
        (item) => this.getFilterName(item) === this.current
      );
    },
    currentDisplayName() {
      return (
        (this.currentItem && this.getFilterDisplayName(this.currentItem)) ||
        this.title
      );
    },
  },
  mounted() {
    this.$watch("filters", this.setWidth, {
      deep: true,
      initial: true,
    });
  },
  methods: {
    measureText(text) {
      const computedStyle = window.getComputedStyle(this.$el);
      const el = document.createElement("span");
      el.style.opacity = "0";
      el.style.position = "absolute";
      el.textContent = text;
      [
        "fontSize",
        "fontFamily",
        "fontWeight",
        "fontStyle",
        "lineHeight",
      ].forEach((key) => {
        el.style[key] = computedStyle[key];
      });

      document.body.appendChild(el);
      const value = el.clientWidth;
      document.body.removeChild(el);

      return value;
    },
    setWidth() {
      this.width = this.measureText(this.currentDisplayName) + 25 + "px";
    },
    setFilter(e) {
      const select = e.target;
      this.filters[this.filter] = select.value || null;
    },
    getFilterDisplayName(item) {
      if (typeof item === "string") {
        return item;
      } else {
        return item.name;
      }
    },
    getFilterName(item) {
      if (typeof item === "string") {
        return item;
      } else if (
        this.filter === "beneficiary" ||
        this.filter === "donor" ||
        this.filter === "sdg_no"
      ) {
        // special case for country filters
        return item.id;
      } else {
        return item.name;
      }
    },
  },
};
</script>

<style lang="less">
@import "@css/style";

.dataviz .viz-select {
  border-color: @bg_color;
  background: @bg_color;
  color: #aaa;
  font-family: inherit;
  max-width: 100%;
  margin-bottom: 2rem !important;
  &:focus {
    outline: none;
  }
  option {
    color: black;
  }
  @media (min-width: 780px) and (max-width: 1000px) {
    width: 100%;
  }
}

.dropdown {
  @media (max-width: 950px) {
    width: 100%;
  }
}

body.dark.dataviz .viz-select {
  border-color: @dark_bg_color;
  background: @dark_bg_color;
  color: #555;

  option {
    color: white;
  }
}
</style>

