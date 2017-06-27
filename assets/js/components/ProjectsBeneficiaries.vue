<script>
import Beneficiaries from './Beneficiaries';
import ProjectsMixin from './mixins/Projects';


export default Beneficiaries.extend({
  mixins: [ProjectsMixin],

  methods: {
    tooltipTemplate(d) {
      // TODO: oh my, the copy-paste. it hurts.
      const data = d.data
                    .filter( (x) => x.value != 0 );
      const datatxt = data
        .map( (x) => `
          <dl>
            <dt>${ x.name }</dt>
            <dd>${ this.number(x.project_count) } projects</dd>
            <dd>${ this.currency(x.value) } gross allocation</dd>
          </dl>
        ` )
        .join("");

      return `
        <div class="title-container">
          <img src="/assets/imgs/${this.get_flag_name(d.id)}.png" />
          <span class="name">${d.name}</span>
        </div>
        ${ datatxt }
        <span class="action">Click to filter by beneficiary state</span>`;
    },
  }
});
</script>
