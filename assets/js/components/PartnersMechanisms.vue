<script>
import Mechanisms from './Mechanisms';
import PartnersMixin from './mixins/Partners';


export default Mechanisms.extend({
  mixins: [PartnersMixin],

  methods: {
    tooltipTemplate(d) {
      // TODO: this is silly. turn this into a component.
      return `
        <div class="title-container">
          <span class="name">${d.name}</span>
        </div>
        <ul>
          <li>${this.number(d.project_count)} projects</li>
          <li>${this.currency(d.value)} gross allocation</li>
          <li>${d.beneficiaries.size()} beneficiary states</li>
          <li>${d.sectors.size()} priority sectors</li>
          <li>${d.areas.size()} programme areas</li>
          <li>${d.programmes.size()} programmes</li>
        </ul>
        <span class="action">Click to filter by financial mechanism</span>
      `;
    },
  }
});
</script>
