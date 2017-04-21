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

      d3.csv(this.datasource, this.processRow, (error, ds) => {
        if (error) throw error;
        this.dataset = this.processDataset(ds);
      });
    },

    processRow(d, i, columns) {
      return d;
    },
  }
};
</script>
