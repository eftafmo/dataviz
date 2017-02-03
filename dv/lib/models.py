import logging
from django.db import models
from django.db.models.base import ModelBase
from dv.lib import utils


logger = logging.getLogger()

_ass_cache = {}


class ImportableModelMixin(object):
    IMPORT_SOURCE = None
    #: a dictionary of either
    #: <model field name>: <imported column name>, or
    #: <model field name>: (<related-model field name>, <imported column name>)
    IMPORT_MAPPING = {}

    @classmethod
    def from_data(cls, data, **values):
        """
        Creates a new object from the given data, handling CamelCased columns.
        Column mapping can be overriden using `cls.IMPORT_MAPPING`.
        Default values can be specified as **kwargs.
        """
        # make a copy, 'cause we'll mutate the input data
        data = data.copy()

        fields = {
            f.name: f
            for f in cls._meta.fields
        }

        def _assign(fld, val, rel_field=None):
            field = fields[fld]

            # quit early for null values
            if val is None and field.null:
                values[fld] = None
                return

            if not field.is_relation:
                # direct assignment?
                if field.choices:
                    # this logic is based on the assumption that the choices are
                    # a `model_utils.Choices` instance, and on the convention
                    # that the choices' "constant name" is derived from the data
                    val = getattr(field.choices,
                                  utils.str_to_constant_name(val))
                else:
                    # avoid writing nulls in fields that don't support it
                    if val is None and not field.null and isinstance(
                            field, (models.CharField, models.TextField)):
                        val = ''
                values[fld] = val
                return

            # else...
            relobjs = field.related_model.objects

            if field.many_to_one:
                # this is a foreign key
                if rel_field:
                    values[fld] = relobjs.get(**{rel_field: val})
                else:
                    values[fld] = relobjs.get_by_natural_key(val)

            elif field.many_to_many:
                # input data must be an iterable
                if rel_field:
                    lookup = "%s__in" % rel_field
                    values[fld] = relobjs.filter(**{lookup: val})
                else:
                    values[fld] = relobjs.filter_by_natural_keys(val)

            else:
                raise NotImplementedError("Can't handle relation type for field", field)

        # first handle everything defined under IMPORT_MAPPING
        for field, column in cls.IMPORT_MAPPING.items():
            # the "column" can in fact be a tuple of (related field, input column)
            rel_field = None
            if isinstance(column, (tuple, list)):
                rel_field, column = column

            try:
                val = data.pop(column)
            except KeyError:
                continue
            else:
                _assign(field, val, rel_field)


        # and finally auto-match all left-overs
        for k in list(data.keys()):
            # convert the input data keys to camel_cased
            k_ = utils.camel_case_to__(k)
            if k_ == k:
                continue
            data[k_] = data.pop(k)

        for field in fields.keys():
            if field in values:
                continue

            try:
                val = data.pop(field)
            except KeyError:
                continue
            else:
                _assign(field, val)

        if data:
            logger.debug("Unused input data: %s", data.keys())
        return cls(**values)
