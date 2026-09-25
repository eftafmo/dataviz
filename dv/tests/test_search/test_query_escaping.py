from django.test import SimpleTestCase
from haystack.query import SearchQuerySet


class TestInFilterEscaping(SimpleTestCase):
    def build(self, **filters):
        return SearchQuerySet().filter(**filters).query.build_query()

    def test_plain_values(self):
        self.assertEqual(
            self.build(state_name__in=["Poland", "Czech Republic"]),
            'state_name:("Poland" OR "Czech Republic")',
        )

    def test_double_quote_is_escaped(self):
        self.assertEqual(
            self.build(period__in=["x'\"(){}<x>:/x;9"]),
            'period:("x\'\\"(){}<x>:/x;9")',
        )

    def test_backslash_is_escaped(self):
        self.assertEqual(
            self.build(period__in=['a\\"b']),
            'period:("a\\\\\\"b")',
        )
