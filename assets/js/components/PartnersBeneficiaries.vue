<script>
import Beneficiaries from './Beneficiaries';
import PartnersMixin from './mixins/Partners';


export default Beneficiaries.extend({
  mixins: [PartnersMixin],

  data() {
    return {
      title: 'Organizations with donor partner by beneficiary'
    }
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
    tooltipTemplate(d) {
      // TODO: oh my, the copy-paste. it hurts.
      const data = d.data
                    .filter( (x) => x.value != 0 );
      const datatxt = data
        .map( (x) => `
            <ul>${ x.name } : ${ this.number(x.project_count) } projects</ul>
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
