<script>
export default {
  mounted() {
    this.createTooltip();
  },

  methods: {
    createTooltip() {
      throw "Not Implemented";
    },
    hungaryTooltipTemplate() {
      return `
      <div class="title-container">
        <img src="${this.get_flag("HU")}" alt=""/>
        <span class="name">Hungary</span>
      </div>
      <div>
        Iceland, Liechtenstein and Norway, did not reach an agreement with Hungary
        on civil society funding. Therefore, no programmes will be implemented in
        Hungary under the EEA and Norway Grants during the 2014-2021
        funding period.
      </div>
      `;
    },
  },
};
</script>

<style lang="less">
@import "@css/style";

.dataviz-tooltip {
  li {
    list-style-type: none;
  }

  ul {
    padding-left: 0;
    margin: 0.5rem 0.5rem 1rem;
  }
  z-index: 2;
  min-width: 320px;
  max-width: 420px;
  padding: 1rem 2rem;
  background-color: fadeout(@bg_color, 0);
  box-shadow: 0 0 3px @shadow_color;
  .btn {
    position: absolute;
    top: 10px;
    right: 15px;
    @media (min-width: 768px) {
      display: none;
    }
  }
  @media (max-width: 768px) {
    display: none;
    left: 0 !important;
    right: 0 !important;
    border: 1px solid #3d90f3;
  }

  &:after {
    content: "▼";
    position: absolute;
    left: 45%;
    bottom: 20px;
    width: 0;
    height: 0;
    color: white;
    text-shadow: 0 2px 3px @shadow_color;
    font-size: 2em;
    clear: both;
    pointer-events: none;
    @media (max-width: 768px) {
      display: none;
    }
  }

  .action {
    font-weight: 400;
    color: #aaa;
    font-size: 12px;
    display: block;
    margin-top: 1rem;
    text-align: right;

    &:before {
      content: "- ";
    }
  }

  .title-container {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding-bottom: 1rem;
    font-weight: 600;
    margin: 0.5rem 0.5rem 1rem;
    border-bottom: 1px solid #eee;
    &.donor-tooltip {
      border-bottom: none;
    }
    img {
      max-width: 30px;
      box-shadow: 0 0 2px #aaa;
      height: 20px;
    }

    span {
      white-space: normal;
    }
  }

  .spacing {
    margin: 0.6rem 0;
    display: block;
  }

  .name {
    margin: 0 0.5rem;
    font-size: 1.8rem;
  }

  .legend-container {
    display: grid;
    grid-gap: 1rem;
    font-size: 1.5rem;
    grid-template-columns: min-content 1fr 1fr;
    font-weight: normal;
  }

  .muted {
    color: #666666;
  }
}
</style>
