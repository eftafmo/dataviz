<script>
import Sectors from './Sectors';
import ProjectsMixin from './mixins/Projects';


export default Sectors.extend({
  mixins: [ProjectsMixin],

  methods: {
    value(item) {
      return this.number(item.data.project_count) + "\u202f" + // narrow nbsp
             "projects";
      //"\u00a0" nbsp
    },

    tooltipTemplate(d) {
      // TODO: such horribleness. sad face.
      const thing = d.depth == 1 ? "sector" : "programme area";
      const num_bs = Object.keys(d.data.beneficiaries).length;
      const num_prg = Object.keys(d.data.programmes).length;

      return `
        <div class="title-container">
          <span>${ d.data.name }</span>
        </div>
        <ul>
          <li>${ this.number(d.data.project_count) } projects</li>
          <li>${ this.currency(d.value) }</li>
          <li>${num_bs} `+  this.singularize(`beneficiary states`, num_bs) + `</li>
          <li>${num_prg}  `+  this.singularize(`programmes`, num_prg) + `</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },
  }
});
</script>
