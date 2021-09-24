<!-- for use with StatesBarChart components -->
<script>
import * as d3 from "d3";

export default {
  computed: {
    types() {
      const types = {};

      for (const k in this.columns) {
        const col = this.columns[k];

        types[k] = Object.assign(
          {
            id: k,
            color: this.colors[k],
          },
          col
        );
      }

      return types;
    },

    div_types() {
      return Object.values(this.types);
    },
  },
  created() {
    for (const k in this.columns) {
      this.aggregate_on.push(this.columns[k]);
    }
  },

  methods: {
    valuefunc(item, type) {
      const orgs = item[this.types[type].source]; // this is a set
      return orgs ? orgs.size : 0;
    },

    tooltipTemplate(ev, d) {
      const data = d.data.filter((x) => x.value != 0);
      const datatxt = data
        .map(
          (x) => `
            <li>${this.number(x.value)} ${this.singularize(
            x.name,
            x.value
          )}</li>
        `
        )
        .join("");

      return `
        <div class="title-container">
          <img src="${this.get_flag(d.id)}" alt=""/>
          <span class="name">${d.name}</span>
        </div>
        <ul> ${datatxt} </ul>
        <span class="action">Click to filter by ${
          this.state_type
        } state</span>`;
    },
  },
};
</script>
