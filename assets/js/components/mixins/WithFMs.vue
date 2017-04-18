<script>
import * as d3 from 'd3';

import {FMColours} from 'js/constants';


export default {
  methods: {
    colour: d3.scaleOrdinal()
      .domain(d3.keys(FMColours))
      .range(d3.values(FMColours)),
  },
};
</script>
