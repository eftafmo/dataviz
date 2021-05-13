<script>
import * as d3 from 'd3';
import {slugify} from '@js/lib/util'

import Sectors from './Sectors';
import PartnersMixin from './mixins/Partners';
import {COUNTRIES} from './mixins/WithCountries';


export default {
  extends: Sectors,
  mixins: [PartnersMixin],

  data(){
    return {
    }
  },

  computed: {
    programme_counts() {
      // this data-shuffling is needed because a single programme can belong
      // to multiple areas, which leads to pie chart distortions.
      const out = {}

      for (const sname in this.aggregated) {
        const sector = this.aggregated[sname],
              sid = slugify(sname)

        // take into account the difference caused by duplicate programmes
        // and condense all areas proportionally

        const programmeset = new Set(),
              values = {}
        let sum = 0

        for (const aname in sector) {
          const area = sector[aname],
                aid = area.id,
                value = area.programmes.size

          values[aid] = value
          sum += value
          area.programmes.each(p => programmeset.add(p))
        }

        const count = programmeset.size

        if (count !== sum) {
          const ratio = count / sum

          for (const aid in values) {
            values[aid] = values[aid] * ratio
          }
        }

        out[sid] = {
          value: count,
          areas: values,
        }
      }

      return out
    },
  },

  methods: {
    valuefunc(d) {
      if (this.isRoot(d) || this.isRogue(d) || this.isSector(d))
        return 0

      if (!this.isEnabled(d)) return 0

      // is this a rogue area?
      if (d.programmes === undefined) return 0

      return this.programme_counts[d.parentid].areas[d.id]
    },

    display(item) {
      // customer has requested not to show the programme count in the legend
      return "";
    },

    tooltipTemplate(d) {
      // TODO: such horribleness. sad face.
      let thing = "programme area",
          value,
          dss = d.data.donors,
          bss = d.data.beneficiaries;

      if(d.depth == 1) {
        thing = "sector";
        value = this.programme_counts[d.data.id].value
        dss = new Set()
        bss = new Set();

        for (const c of d.children) {
          if (c.data.donors)
            for (const ds of c.data.donors.values())
              dss.add(ds);
          if (c.data.beneficiaries)
            for (const bs of c.data.beneficiaries.values())
              bss.add(bs);
        }
      } else {
        value = d.data.programmes.size
      }

      const num_bs = bss.size;
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
          <li>${value}\u00a0` + this.singularize("programmes", value) + `</li>
          <li>${num_bs} `+  this.singularize(`beneficiary states`, num_bs) + `</li>
        </ul>
        <span class="action">Click to filter by ${ thing }</span>
      `;
    },
  }
}
</script>
