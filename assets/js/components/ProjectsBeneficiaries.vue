<script>
import Beneficiaries from './Beneficiaries';
import ProjectsMixin from './mixins/Projects';

import Legend from './includes/Legend';


export default {
  extends: Beneficiaries,
  mixins: [
    ProjectsMixin,
  ],

  data() {
    return {
    }
  },

  computed: {
    legendFormatFunc() {
      return v => this.number(v) + " " + this.pluralize("project", v)
    },
  },

  methods: {
    valuefunc(item, fm) {
      fm = this.FMS[fm]
      return this.isDisabledFm(fm) ? 0 : (item[fm.name] ? item[fm.name].project_allocation : 0)
    },

    totalvaluefunc(v) {
      return v ? v.project_count : 0
    },

    tooltipTemplate(d) {
      // TODO: oh my, the copy-paste. it hurts.
      const data = d.data
                    .filter( (x) => x.value != 0 );
      const datatxt = data
        .map( (x) => `
            <ul>${ x.name } : ${ this.number(d[x.name].project_count) } projects</ul>
        ` )
        .join("");

      return `
        <div class="title-container">
          <svg>
            <use xlink:href="#${this.get_flag_name(d.id)}" />
          </svg>
          <span class="name">${d.name}</span>
        </div>
        <ul> ${ datatxt } </ul>
        <span class="action">Click to filter by beneficiary state</span>`;
    },
  }
}
</script>
