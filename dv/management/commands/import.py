import io
import logging
import pickle
import pyexcel
import os.path
import zipfile
from functools import partial
from itertools import cycle
from urllib.parse import urlparse
from urllib.request import urlopen

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from dv.models import (
    NUTS,
    State, PrioritySector, ProgrammeArea, Programme, Programme_ProgrammeArea,
    Outcome, ProgrammeOutcome, Project, ProjectTheme, Indicator, ProgrammeIndicator,
    OrganisationType, Organisation, OrganisationRole,
    FinancialMechanism, Allocation, Organisation_OrganisationRole)
from dv.lib.utils import is_iter

logger = logging.getLogger()

NUTS_FILE = "http://ec.europa.eu/eurostat/ramon/documents/nuts/NUTS_2006.zip"


class Command(BaseCommand):
    help = 'Import the file given as argument'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            help="a spreadsheet file. xlsx is supported")

    def handle(self, *args, **options):
        fname = options['file']
        if not os.path.exists(fname):
            raise CommandError('Cannot open file "%s".' % fname)

        # TODO: use the cache dir here.
        cname = fname + '.cache'
        if os.path.exists(cname):
            with open(cname, 'rb') as cached:
                book = pickle.load(cached)
        else:
            book = pyexcel.get_book(file_name=fname)
            with open(cname, 'wb') as cached:
                pickle.dump(book, cached)

        # momentarily using the other file's directory for caching
        fname = os.path.join(
            os.path.dirname(fname),
            os.path.basename(urlparse(NUTS_FILE).path)
        )
        cname = fname + '.cache'
        if os.path.exists(cname):
            with open(cname, 'rb') as cached:
                nuts_book = pickle.load(cached)
        else:
            with urlopen(NUTS_FILE) as f:
                with zipfile.ZipFile(io.BytesIO(f.read())) as z:
                    zf = z.namelist()[0]
                    nuts_book = pyexcel.get_book(file_content=z.open(zf).read(),
                                                 file_type=zf.split('.')[-1])
            with open(cname, 'wb') as cached:
                pickle.dump(nuts_book, cached)

        models = (
            # NUTS,
            State,
            FinancialMechanism,
            PrioritySector,
            ProgrammeArea,
            Allocation,
            Programme,
            Programme_ProgrammeArea,
            Outcome,
            ProgrammeOutcome,
            Project,
            ProjectTheme,
            Indicator,
            ProgrammeIndicator,
            OrganisationType,
            Organisation,
            OrganisationRole,
            Organisation_OrganisationRole,
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

        # column names for nuts
        for sheet in nuts_book:
            sheet.name_columns_by_row(0)

        def _convert_nulls(record):
            for k, v in record.items():
                if v in ('NULL', 'None'):
                    record[k] = None

        for model in models:
            for idx, import_src in enumerate(model.IMPORT_SOURCES):
                sheet_name = import_src['src']
                mapping = import_src['map']
                if model == NUTS:
                    sheet = nuts_book[sheet_name]
                else:
                    sheet = book[sheet_name]

                _inline('importing "%s" into %s …  ' % (sheet.name, model._meta.label))

                count = 0

                def _save(obj):
                    nonlocal count
                    try:
                        obj.save()
                        count += 1
                    except IntegrityError as e:
                        # NOTE This is backend specific; might change on switch, say, postgres
                        if 'UNIQUE constraint failed:' in str(e):
                            pass
                        else:
                            raise

                for record in sheet.records:
                    _inline(next(throbber))
                    _convert_nulls(record)

                    obj = model.from_data(record, idx)
                    if obj is None:
                        # trust the class, it knows why it refused object creation
                        continue

                    if is_iter(obj):
                        for _obj in obj:
                            _save(_obj)
                    else:
                        _save(obj)

                _write(_back + "done: %d" % count, self.style.SUCCESS)

        cache.clear()
        _write(_back + "Cache cleared", self.style.SUCCESS)
