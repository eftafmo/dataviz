import argparse
import pickle
import pyexcel
import os.path
from functools import partial
from itertools import cycle
from django.core.management.base import BaseCommand, CommandError
from dv.models import (
    State, PrioritySector, ProgrammeArea, Programme, Programme_ProgrammeArea,
    Outcome, ProgrammeOutcome, Project, Indicator, ProgrammeIndicator,
    OrganisationType, Organisation, OrganisationRole,
)
from dv.lib.utils import is_iter


class Command(BaseCommand):
    help = 'Import the file given as argument'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            help="a spreadsheet file. xlsx is supported")

    def handle(self, *args, **options):
        fname = options['file']
        if not os.path.exists(fname):
            raise CommandError('Cannot open file "%s".' % fname)

        cname = fname + '.cache'
        if os.path.exists(cname):
            with open(cname, 'rb') as cached:
                book = pickle.load(cached)
        else:
            book = pyexcel.get_book(file_name=fname)
            with open(cached, 'wb') as out:
                pickle.dump(book, cached)

        models = (
            State, PrioritySector, ProgrammeArea, Programme, Programme_ProgrammeArea,
            Outcome, ProgrammeOutcome, Project,
            Indicator, ProgrammeIndicator,
            OrganisationType, Organisation, OrganisationRole,
        )

        self.stderr.style_func = None
        def _write(*args, **kwargs):
            self.stderr.write(*args, **kwargs)
            self.stderr.flush()
        _inline = partial(_write, ending='')
        _back = chr(8)
        throbber = cycle(_back + c for c in r'\|/-')

        # clean up the spreadbook
        for sheet in book:
            # because the real data only starts on the 3rd row
            del sheet.row[1], sheet.row[0]
            # we can now use the first row as the header
            sheet.name_columns_by_row(0)

        def _convert_nulls(record):
            for k, v in record.items():
                if v in ('NULL', 'None'):
                    record[k] = None

        for model in models:
            _inline('importing "%s" into %s …  ' % (model.IMPORT_SOURCE,
                                                    model._meta.label))
            sheet = book[model.IMPORT_SOURCE]


            # we'll often have duplicates in a single sheet,
            # so keep track of uniques
            uniq_field = getattr(model, 'NATURAL_KEY_FIELD', None)
            pk_field = model._meta.pk
            if not uniq_field:
                try:
                    uniq_field = next(f.name
                                      for f in model._meta.fields
                                      if f.unique
                                      and f != pk_field)
                except StopIteration:
                    try:
                        uniq_field = model._meta.unique_together[0]
                    except IndexError:
                        # fallback to pk, and hope for the best
                        uniq_field = pk_field.name

            created = []
            count = 0

            def _save(obj):
                if is_iter(uniq_field):
                    key = tuple(getattr(obj, fld) for fld in uniq_field)
                else:
                    key = getattr(obj, uniq_field)

                if key in created:
                    return
                elif key is None and uniq_field == pk_field.name:
                    # nothing to keep track of
                    pass
                else:
                    created.append(key)

                obj.save()
                nonlocal count
                count += 1

            for record in sheet.records:
                _inline(next(throbber))
                _convert_nulls(record)

                obj = model.from_data(record)
                if obj is None:
                    # trust the class, it knows why it refused object creation
                    continue

                if is_iter(obj):
                    for _obj in obj:
                        _save(_obj)
                else:
                    _save(obj)

            _write(_back + "done: %d" % count, self.style.SUCCESS)
