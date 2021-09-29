<script>
import * as d3 from "d3";

import Sectors from "./Sectors";
import ProjectsMixin from "./mixins/Projects";

export default {
  extends: Sectors,
  mixins: [ProjectsMixin],

  data() {
    return {};
  },

  computed: {
    filtered() {
      // exclude technical assistance sectors from project
      return this.filter(this.dataset, this.filter_by).filter((x) => !x.is_ta);
    },
  },

  methods: {
    display(item) {
      let count;
      if (item.depth === 2) {
        count = item.data.projects.size;
      } else {
        count = new Set(
          item.children
            .filter((child) => !!child.data.projects)
            .map((child) => Array.from(child.data.projects))
            .flat()
        ).size;
      }

      return (
        this.number(count) + "\u00a0" + this.singularize("projects", count)
      );
    },
    displayLong(item) {
      return this.display(item);
    },
    tooltipTemplate(ev, d) {
      // TODO: such horribleness. sad face.
      let thing = "programme area",
        bss = d.data.beneficiaries,
        prgs = d.data.programmes;

      if (d.depth === 1) {
        thing = "sector";
        bss = new Set();
        prgs = new Set();

        for (const c of d.children) {
          if (c.data.beneficiaries)
            for (const bs of c.data.beneficiaries.values()) bss.add(bs);
          if (c.data.programmes)
            for (const prg of c.data.programmes.values()) prgs.add(prg);
        }
      }

      const num_bs = bss.size;
      const num_prg = prgs.size;

      return (
        `
        <div class="title-container">
          <span>${d.data.name}</span>
        </div>
        <ul>
          <li>${this.display(d)}</li>
          <li>${this.currency(d.value)} net allocation</li>
          <li>${num_bs} ` +
        this.singularize(`Beneficiary States`, num_bs) +
        `</li>
          <li>${num_prg}  ` +
        this.singularize(`programmes`, num_prg) +
        `</li>
        </ul>
        <span class="action">Click to filter by ${thing}</span>
      `
      );
    },
  },
};
</script>
