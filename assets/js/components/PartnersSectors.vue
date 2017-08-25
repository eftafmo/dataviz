<script>
import * as d3 from 'd3';

import Sectors from './Sectors';
import PartnersMixin from './mixins/Partners';
import {COUNTRIES} from './mixins/WithCountries';


export default Sectors.extend({
  mixins: [PartnersMixin],

  data(){
    return {
    }
  },

  updated() {
    let dropdown = this.$el.querySelector('.viz-select');
    if(!dropdown) return;
    dropdown.style.cssFloat = 'initial'
    dropdown.style.marginBottom = '4rem'
    let title = this.$el.querySelector('h2')
    if(!title) return;
    title.style.marginBottom = '1rem'
  },

  methods: {
    valuefunc(d) {
      if (this.isRoot(d) || this.isRogue(d))
        return 0

      if (!this.isEnabled(d)) return 0

      if (this.isSector(d)) {
        // get rid of the doubly-counted programmes
        const all = d3.set()
        let sum = 0

        for (const aid in d.children) {
          const prgs = d.children[aid].programmes
          if (prgs === undefined) continue

          prgs.each( x => all.add(x) )
          sum += prgs.size()
        }
        return all.size() - sum
      }

      // is this a rogue area?
      if (d.programmes === undefined) return 0
      return d.programmes.size()
    },

    display(item) {
      // customer has requested not to show the programme count in the legend
      return "";
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
      // sort donor states
      const ds_sorted = dss.values().sort(
        (a,b) => d3.ascending(COUNTRIES[a].sort_order, COUNTRIES[b].sort_order)
      ).map(
        code => COUNTRIES[code].name
      ).join(", ");

      return `
        <div class="title-container">
          <span>${ d.data.name }</span>
        </div>
        <ul>
          <li>Donor states: ${ds_sorted}</li>
          <li>${d.value}\u00a0` + this.singularize("programmes", d.value) + `</li>
          <li>${num_bs} `+  this.singularize(`beneficiary states`, num_bs) + `</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },
  }
});
</script>
