<script>
/*
 * Use this when the datasource is a CSV,
 * after Base.
 */

import * as d3 from 'd3';

export default {
  methods: {
    fetchData() {
      if (!this.datasource) throw "Missing datasource."
      const $this = this;

      d3.csv($this.datasource, this.processRow, function(error, data) {
        if (error) throw error;
        $this.data = $this.processData(data);
      });
    },

    processRow(d, i, columns) {
      return d;
    },
  }
};
</script>
