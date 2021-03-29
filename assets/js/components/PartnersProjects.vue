<script>
import Projects from "./Projects";
import Programmes from "./Programmes";
import PartnersMixin from "./mixins/Partners";

const PartnersProgrammes = Programmes.extend({
  mixins: [PartnersMixin],
});

export default Projects.extend({
  components: {
    programmes: PartnersProgrammes,
  },

  data() {
    return {
      extra: "is_dpp=True",
    };
  },
});
</script>
