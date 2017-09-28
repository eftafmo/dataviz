import logging
import pickle
import pyexcel
import os.path
from functools import partial
from itertools import cycle

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.db import IntegrityError

from dv.models import (
    State, PrioritySector, ProgrammeArea, Programme, Programme_ProgrammeArea,
    Outcome, ProgrammeOutcome, Project, ProjectTheme, Indicator, ProgrammeIndicator,
    OrganisationType, Organisation, OrganisationRole,
    FinancialMechanism, Allocation, Organisation_OrganisationRole)
from dv.lib.utils import is_iter

logger = logging.getLogger()

EXCEL_FILES = (
    'BeneficiaryState',
    'BeneficiaryStatePrioritySector',
    'Programme',
    'ProgrammeOutcome',
    'Project',
    'ProjectThemes',
    'ProgrammeIndicators',
    'Organisation',
    'OrganisationRoles',
)

MODELS = (
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


class Command(BaseCommand):
    help = 'Import the files in the directory given as argument'

    def add_arguments(self, parser):
        parser.add_argument('directory',
                            help="a directory containing spreadsheet files. xlsx and "
                                 "xls is are supported")

    def handle(self, *args, **options):
        directory_path = options['directory']
        if not os.path.exists(directory_path):
            raise CommandError('Cannot open directory "%s".' % directory_path)

        files = os.listdir(directory_path)
        if not files:
            raise CommandError('Directory %s is empty' % directory_path)

        existing_books = [file.split('.')[0] for file in files]
        for file in EXCEL_FILES:
            if file not in existing_books:
                raise CommandError('%s workbook is missing' % file)

        sheets = dict()

        cached_directory = (
            directory_path if directory_path[-1] != '/' else directory_path[:-1]
        ) + '.cache'
        if os.path.exists(cached_directory):
            for file in files:
                file_path = os.path.join(cached_directory, file)
                with open(file_path, 'rb') as cached:
                    book = pickle.load(cached)
                    sheets[file.split('.')[0]] = book['Sheet1']
        else:
            os.makedirs(cached_directory)
            for file in files:
                file_path = os.path.join(directory_path, file)
                cached_file_path = os.path.join(cached_directory, file)
                book = pyexcel.get_book(file_name=file_path)
                sheets[file.split('.')[0]] = book['Sheet1']
                with open(cached_file_path, 'wb') as cached:
                    pickle.dump(book, cached)

        for sheet in sheets.values():
            sheet.name_columns_by_row(0)

        self.stderr.style_func = None

        def _write(*args, **kwargs):
            self.stderr.write(*args, **kwargs)
            self.stderr.flush()
        _inline = partial(_write, ending='')
        _back = chr(8)
        throbber = cycle(_back + c for c in r'\|/-')

        def _convert_nulls(record):
            for k, v in record.items():
                if v in ('NULL', 'None'):
                    record[k] = None

        for model in MODELS:
            for idx, import_src in enumerate(model.IMPORT_SOURCES):
                sheet_name = import_src['src']
                sheet = sheets[sheet_name]

                _inline('importing "%s" into %s …  ' % (sheet_name, model._meta.label))

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
