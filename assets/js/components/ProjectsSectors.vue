<script>
import Sectors from './Sectors';
import ProjectsMixin from './mixins/Projects';


export default Sectors.extend({
  mixins: [ProjectsMixin],

  methods: {
    tooltipTemplate(d) {
      // TODO: such horribleness. sad face.
      const thing = d.depth == 1 ? "priority sector" : "programme area";

      return `
        <div class="title-container">
          <span>${ d.data.name }</span>
        </div>
        <ul>
          <li>${ this.number(d.data.project_count) } projects</li>
          <li>${ this.currency(d.value) } grant allocation</li>
        </ul>
        <span class="action">~Click to filter by ${ thing }</span>
        <button class="btn btn-anchor">X</button>
      `;
    },
  }
});
</script>
