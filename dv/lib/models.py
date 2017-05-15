import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from enumfields import EnumField
from dv.lib import utils


logger = logging.getLogger()


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
                if isinstance(field, EnumField):
                    # we replaced model_utils.choices with enumfields.EnumField,
                    # so below doesn't really apply

                    # TODO: this is pretty. pretty ugly.
                    val = getattr(type(field.choices[0][0]),
                                  utils.str_to_constant_name(val))
                elif field.choices:
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
                # TODO trimm ws?
                val = data.pop(column)
            except KeyError:
                logger.error("Column %s not found in sheet %s", column, cls.IMPORT_SOURCE)
                raise
            else:
                try:
                    _assign(field, val, rel_field)
                except ObjectDoesNotExist as e:
                    logger.warning("Error while assigning val: {} to field: {}, rel_field: {} ({})".format(val, field, rel_field, e))

        if data:
            logger.debug("Unused input data: %s", data.keys())
        return cls(**values)
