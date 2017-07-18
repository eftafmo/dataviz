<script>
import Beneficiaries from './Beneficiaries';
import PartnersMixin from './mixins/Partners';


export default Beneficiaries.extend({
  mixins: [PartnersMixin],

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
