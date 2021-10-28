<script>
import GrantsMap from "./GrantsMap";

export default {
  name: "GlobalGoalsMap",
  extends: GrantsMap,
  data() {
    return {
      allocationType: "net",
      aggregate_on: [
        "allocation",
        "net_allocation",
        {
          source: "beneficiary",
          destination: "beneficiaries",
          type: String,
          exclude: "is_ta",
        },
        {
          source: "sectors",
          destination: "sectors",
          type: Array,
          exclude: "is_ta",
        },
        {
          source: "areas",
          destination: "areas",
          type: Array,
          exclude: "is_ta",
        },
        { source: "programmes", type: Object },
      ],
    };
  },
  methods: {
    tooltipTemplate(ev, d) {
      const allocation = d.allocation || 0,
        country_is_donor =
          d.id.length === 2 && this.COUNTRIES[d.id].type === "donor",
        state_type = country_is_donor ? "donor-tooltip" : "";

      let region_name;
      let extra = "";
      if (d.id.length === 2) {
        region_name = this.COUNTRIES[d.id].name;
        extra = `
          <li>
            ${this.currency(allocation)} ${this.allocationType} allocation
          </li>
        `;
      } else {
        region_name = this.getRegionName(d.id) + "(" + d.id + ")";
      }

      const get_amount = (s) => (s === undefined ? 0 : s.size),
        country_details = country_is_donor
          ? ""
          : `
              <ul>
                ${extra}
                <li>${get_amount(d.sectors)} ` +
            this.singularize(`sectors`, get_amount(d.sectors)) +
            `</li>
                <li>${get_amount(d.areas)} ` +
            this.singularize(`programme areas`, get_amount(d.areas)) +
            `</li>
                <li>${get_amount(d.programmes)}  ` +
            (get_amount(d.programmes) === 1
              ? "programme/agreement"
              : "programmes and agreements") +
            `</li>
              </ul>
            `;

      return (
        `
        <div class="title-container ${state_type}">
          <img src="${this.get_flag(d.id)}" alt=""/>
          <span class="name">${region_name}</span>
        </div>` + country_details
      );
    },
  },
};
</script>

<style scoped>

</style>
