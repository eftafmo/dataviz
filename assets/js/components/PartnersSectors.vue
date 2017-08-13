<script>
import * as d3 from 'd3';

import Sectors from './Sectors';
import PartnersMixin from './mixins/Partners';
import {COUNTRIES} from './mixins/WithCountries';


export default Sectors.extend({
  mixins: [PartnersMixin],

  data(){
    return {
      title: 'Donor partner programmes by priority sector',
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
          dss = d.data.donors,
          bss = d.data.beneficiaries;

      if(d.depth == 1) {
        thing = "sector";
        dss = d3.set()
        bss = d3.set();

        for (const c of d.children) {
          if (c.data.donors)
            for (const ds of c.data.donors.values())
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
          <li>Donor states: ${dss.values().map(x => COUNTRIES[x].name).join(", ")}</li>
          <li>${ this.display(d) }</li>
          <li>${num_bs} `+  this.singularize(`beneficiary states`, num_bs) + `</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },
  }
});
</script>
