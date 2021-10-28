<script>
import Projects from "./Projects";
import Programmes from "./Programmes";
import PartnersMixin from "./mixins/Partners";

const PartnersProgrammes = {
  extends: Programmes,
  mixins: [PartnersMixin],

  methods: {
    getCountryCount(beneficiary) {
      return `${beneficiary.dpp_projects_count} projects with Donor partners`;
    },
  },
};

export default {
  components: {
    programmes: PartnersProgrammes,
  },
  extends: Projects,

  data() {
    return {
      extra: "is_dpp=True",
    };
  },
};
</script>
