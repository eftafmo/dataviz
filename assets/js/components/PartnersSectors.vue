<script>
import Sectors from './Sectors';
import PartnersMixin from './mixins/Partners';


export default Sectors.extend({
  mixins: [PartnersMixin],

  methods: {
    value(item) {
      return this.number(item.data.project_count) + "\u202f" + // narrow nbsp
             "projects";
      //"\u00a0" nbsp
    },

    tooltipTemplate(d) {
      // TODO: such horribleness. sad face.
      const thing = d.depth == 1 ? "priority sector" : "programme area";

      return `
        <div class="title-container">
          <span>${ d.data.name }</span>
        </div>
        <ul>
          <li>${ this.number(d.data.project_count) } projects</li>
          <li>${ this.currency(d.value) } gross allocation</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },
  }
});
</script>
