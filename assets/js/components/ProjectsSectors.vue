<script>
import * as d3 from 'd3';

import Sectors from './Sectors';
import ProjectsMixin from './mixins/Projects';


export default Sectors.extend({
  mixins: [ProjectsMixin],

  data(){
    return {
      title: 'Projects by sector'
    }
  },

  methods: {
    display(item) {
      const count = item.depth == 2 ? item.data.project_count :
                    d3.sum(item.children, x => x.data.project_count);

      return this.number(count) + "\u00a0" +
             this.singularize("projects", count);
    },

    tooltipTemplate(d) {
      // TODO: such horribleness. sad face.
      let thing = "programme area",
          bss = d.data.beneficiaries,
          prgs = d.data.programmes;

      if(d.depth == 1) {
        thing = "sector";
        bss = d3.set();
        prgs = d3.set();

        for (const c of d.children) {
          if (c.data.beneficiaries)
            for (const bs of c.data.beneficiaries.values())
              bss.add(bs);
          if (c.data.programmes)
            for (const prg of c.data.programmes.values())
              prgs.add(prg);
        }
      }

      const num_bs = bss.size();
      const num_prg = prgs.size();

      return `
        <div class="title-container">
          <span>${ d.data.name }</span>
        </div>
        <ul>
          <li>${ this.display(d) }</li>
          <li>${ this.currency(d.value) } gross allocation</li>
          <li>${num_bs} `+  this.singularize(`beneficiary states`, num_bs) + `</li>
          <li>${num_prg}  `+  this.singularize(`programmes`, num_prg) + `</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },
  }
});
</script>
