<script>
import StatesBarChart from './StatesBarChart';

import PartnersMixin from './mixins/Partners';
import BeneficiariesMixin from './mixins/BeneficiariesBarChart';


export default StatesBarChart.extend({
  mixins: [
    PartnersMixin,
    BeneficiariesMixin,
  ],

  data() {
    return {
      title: 'Organizations with donor partner by beneficiary state'
    }
  },

  created() {
    for (const col of [
      {source: "programme_operators",
       destination: this.types.programmes.column,
       type: Object},
      {source: "project_promoters",
       destination: this.types.projects.column,
       type: Object},
    ])
      this.aggregate_on.push(col)
  },

  computed: {
    div_types() {
      const base = {
        programmes: {
          name: "Programme organisations",
          column: "programme_orgs",
        },

        projects: {
          name: "Project organisations",
          column: "project_orgs",
        },
      }

      const types = []

      for (const k in base) {
        types.push(Object.assign({
          id: k,
          colour: this.colours[k],
        }, base[k]))
      }

      return types
    },
    types() {
      // the same thing, but as a dict
      const out = {}
      for (const type of this.div_types) {
        out[type.id] = type
      }
      return out
    },
  },

  updated() {
    let dropdown = this.$el.querySelector('.viz-select');
    let title = this.$el.querySelector('h2')
    if(!dropdown) return;
    dropdown.style.cssFloat = 'initial'
    dropdown.style.marginBottom = '4rem'
    title.style.marginBottom = '1rem'
  },

  methods: {
    valuefunc(item, type) {
      const orgs = item[this.types[type].column] // this is a set
      return orgs ? orgs.size() : 0
    },

    tooltipTemplate(d) {
      const data = d.data
                    .filter( (x) => x.value != 0 );
      const datatxt = data
        .map( (x) => `
            <ul>${ this.number(x.value) } ${ x.name }</ul>
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
  }
});
</script>
