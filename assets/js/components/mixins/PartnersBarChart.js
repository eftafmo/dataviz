// for use with StatesBarChart components
import * as d3 from 'd3';


export default {
  created() {
    for (const k in this.columns) {
      const col = this.columns[k]

      this.aggregate_on.push(Object.assign({
        type: Object,
      }, col))
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
      return d3.values(this.types)
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
            <ul>${ this.number(x.value) } ${ x.label }</ul>
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
        <span class="action">Click to filter by beneficiary state</span>`;
    },
  },
};
