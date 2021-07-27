<script>
import Projects from "./Projects";
import Programmes from "./Programmes";
import PartnersMixin from "./mixins/Partners";

const PartnersProgrammes = {
  extends: Programmes,
  mixins: [PartnersMixin],
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
