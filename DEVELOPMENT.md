
# Assets folders

## JS

/components : large site components (content islands), coded in vue
  /mixins : used as building blocks for the other components
  /includes : components of the components, that aren't necessarily widgets
/widgets : small vue components, usually registered globally


# Anatomy of a component

Important properties:

- datasource: prop
  url of source data;
- initial: prop
  initial data, can be passed in by template;
- dataset: data
  either equivalent to `initial` (but mutable),
  or obtained from the datasource;
- data: computed
  obtained by processing (and filtering) the dataset.

Important methods:
- processDataset():
  does preliminary processing of the received data. its output is assigned
  to the `datasource` property;
- processRow():
  only available to CSV-based components. does per-row pre-processing;
