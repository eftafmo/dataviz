<script>
import * as d3 from 'd3';

import Sectors from './Sectors';
import PartnersMixin from './mixins/Partners';


export default Sectors.extend({
  mixins: [PartnersMixin],

  data(){
    return {
      title: 'Donor partner programmes by priority sector'
    }
  },


  methods: {
    value(d) {
      return d.partnership_programmes === undefined ?
             0 : d.partnership_programmes.size();
    },

    display(item) {
      return this.number(item.value) + "\u00a0" +
             this.singularize("programmes", item.value);
    },

    tooltipTemplate(d) {
      // TODO: such horribleness. sad face.

      let thing = "programme area",
          dss = d.data.donor_states,
          bss = d.data.beneficiaries;

      if(d.depth == 1) {
        thing = "sector";
        dss = d3.set()
        bss = d3.set();

        for (const c of d.children) {
          if (c.data.donor_states)
            for (const ds of c.data.donor_states.values())
              dss.add(ds);
          if (c.data.beneficiaries)
            for (const bs of c.data.beneficiaries.values())
              bss.add(bs);
        }
      }

      const num_bs = bss.size();

      return `
        <div class="title-container">
          <span>${ d.data.name }</span>
        </div>
        <ul>
          <li>${ this.display(d) }</li>
          <li>Donors: ${dss.values().join(", ")}</li>
          <li>${num_bs} `+  this.singularize(`beneficiary states`, num_bs) + `</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },
  }
});
</script>
