
from haystack.forms import FacetedSearchForm

import logging
logger = logging.getLogger()


class EeaFacetedSearchForm(FacetedSearchForm):

    def __init__(self, *args, **kwargs):
        from .frontend import FacetedSearchView

        data = dict(kwargs.get('data', kwargs.get('initial', {})))
        self.facets = {}
        for facet_name in FacetedSearchView.facet_fields:
            self.facets[facet_name] = data.get(facet_name, [])
        super().__init__(*args, **kwargs)

    # Override this so we have something to stat with
    def no_query_found(self):
        return self.searchqueryset

    def search(self):
        sqs = super().search()
        for facet_name, facet_values in self.facets.items():
            query = ''
            for value in facet_values:
                if query:
                    query += ' OR '
                query += '"{}"'.format(sqs.query.clean(value))
            if query:
                sqs = sqs.narrow('{}:{}'.format(facet_name, query))

        return sqs
