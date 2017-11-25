from haystack.forms import FacetedSearchForm
from haystack.inputs import AltParser

from dv.views.facets_rules import (
    FACET_MIN_COUNT, FACET_LIMIT, FACET_SORT,
)


class EeaFacetedSearchForm(FacetedSearchForm):

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        self.facet_rules = kwargs.pop('facet_rules', {})

        data = dict(kwargs.get('data', initial))
        self.facets = {
            'kind': [kwargs.pop('facet_kind', 'Programme')]
        }
        for facet_name in self.facet_rules.keys():
            self.facets[facet_name] = data.get(facet_name, [])
        super().__init__(*args, **kwargs)

    # Override this so we have something to stat with
    def no_query_found(self):
        return self.searchqueryset

    def alter_or_facets(self, sqs, facet_name, facet_values):
        # Determine operation type - AND/OR supported so far
        operator = self.facet_rules.get(facet_name, None)
        if facet_name == 'kind':
            operator = 'AND'
        if operator not in ['AND', 'OR']:
            return sqs
        query = ''
        for value in facet_values:
            if query:
                query += " {} ".format(operator)
            query += '"{}"'.format(sqs.query.clean(value))
        if query:
            if operator == 'AND':
                sqs = sqs.narrow('{}:({})'.format(facet_name, query))
            elif operator == 'OR':
                # Exclude {facet_name} when calculating facets and counts
                # Note that we are using as key the same facet_name, not a new alias
                # wiki.apache.org/solr/SimpleFacetParameters#Multi-Select_Faceting_and_LocalParams
                # When searching for autocomplete facets, must not filter by itself
                sqs = sqs.narrow('{{!tag={0}}}{0}:({1})'.format(facet_name, query))
                # del sqs.query.facets[facet_name]
                # Don't delete the original facet, no support for tagging/params in facet.mincount
                # Fixes #518
                sqs = sqs.facet(
                    '{{!ex={0} key={0}}}{0}'.format(facet_name),
                    mincount=FACET_MIN_COUNT,
                    limit=FACET_LIMIT,
                    sort=FACET_SORT,
                )
        return sqs

    def search(self):
        try:
            q = self.cleaned_data.pop('q')
        except KeyError:
            pass
        sqs = super().search()
        if q:
            params = {
                'q.op': 'AND'
            }
            # Set default op for multi-word search term
            sqs = sqs.filter(content=AltParser('dismax', q, **params))

        for facet_name, facet_values in self.facets.items():
            sqs = self.alter_or_facets(sqs, facet_name, facet_values)
        return sqs


class EeaAutoFacetedSearchForm(EeaFacetedSearchForm):
    def __init__(self, *args, **kwargs):
        data = dict(kwargs.get('data', kwargs.get('initial', {})))
        self.auto_name = data.pop('auto_name')
        if self.auto_name:
            self.auto_name = self.auto_name[0]
        self.auto_value = data.pop('auto_value', '')
        if self.auto_value:
            self.auto_value = ' '.join(self.auto_value)

        super().__init__(*args, **kwargs)

    def matched_multi_values(self, solr_res, terms):
        vals = set()
        solr_field_val = getattr(solr_res, self.auto_name)
        # reduce to multival
        if not isinstance(solr_field_val, list):
            solr_field_val = [solr_field_val]
        for val in solr_field_val:
            low_val = val.lower()
            for term in terms:
                if term in low_val:
                    vals.add(val)

        return vals

    def search(self):
        sqs = super().search()
        # We do only one autocomplete at a time so there's only one auto field name/value
        # (we type in only one field at a time, select the value desired, then type for a new match)
        if self.auto_name and self.auto_value and len(self.auto_value) >= 2:
            # Remove one-letter words from auto_value because default minGramSize=2 in haystack
            search_term = ' '.join([w for w in self.auto_value.split() if len(w) > 1])
            if search_term:
                kw = {
                    '{}_auto'.format(self.auto_name): search_term
                }
                sqs = sqs.autocomplete(**kw)

        return sqs
