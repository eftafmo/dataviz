<!-- for use with StatesBarChart components -->
<script>
import * as d3 from 'd3';

export default {

  created() {
    for (const k in this.columns) {
      this.aggregate_on.push(this.columns[k])
    }
  },

  computed: {
    types() {
      const types = {}

      for (const k in this.columns) {
        const col = this.columns[k]

        types[k] = Object.assign({
          id: k,
          colour: this.colours[k],
        }, col)
      }

      return types
    },

    div_types() {
      return Object.values(this.types)
    },
  },

  methods: {
    valuefunc(item, type) {
      const orgs = item[this.types[type].source] // this is a set
      return orgs ? orgs.size() : 0
    },

    tooltipTemplate(d) {
      const data = d.data
                    .filter( (x) => x.value != 0 );
      const datatxt = data
        .map( (x) => `
            <li>${ this.number(x.value) } ${ this.singularize(x.name, x.value) }</li>
        ` )
        .join("");

      return `
        <div class="title-container">
          <svg>
            <use xlink:href="#${this.get_flag_name(d.id)}" />
          </svg>
          <span class="name">${d.name}</span>
        </div>
        <ul> ${ datatxt } </ul>
        <span class="action">Click to filter by ${ this.state_type } state</span>`;
    },
  },
};
</script>
