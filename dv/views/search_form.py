from haystack.forms import FacetedSearchForm


class ProgFacetedSearchForm(FacetedSearchForm):

    def __init__(self, *args, **kwargs):
        # data = dict(kwargs.get("data", []))
        data = kwargs.get('data', kwargs.get('initial', {}))
        self.states = data.get('state_name', [])
        self.kind = data.get('kind', 'Programme')
        super().__init__(*args, **kwargs)

    def no_query_found(self):
        return self.searchqueryset

    def search(self):
        sqs = super().search()
        sqs = sqs.narrow('kind:{}'.format(self.kind))
        query = ''
        for st in [self.states] if self.states and isinstance(self.states, str) else self.states:
            if query:
                query += ' OR '
            query += '"{}"'.format(sqs.query.clean(st))
        if query:
            sqs = sqs.narrow('state_name:{}'.format(query))

        return sqs
