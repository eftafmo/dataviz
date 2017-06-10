<script>
import * as d3 from 'd3';

import BaseMap from './BaseMap';
import ProjectsMixin from './mixins/Projects';


export default BaseMap.extend({
  mixins: [
    ProjectsMixin,
  ],
});
</script>
