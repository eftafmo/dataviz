import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from enumfields import EnumField
from dv.lib import utils


logger = logging.getLogger()


class ImportableModelMixin(object):
    IMPORT_SOURCES = [
        {
            'src': None,
            #: a dictionary of either
            #: <model field name>: <imported column name>, in which case 'code' will be looked up, or
            #: <model field name>: (<related-model lookup field name>, <imported column name>)
            'map': {}
        }
    ]

    @classmethod
    def from_data(cls, data, src_idx, **values):
        """
        Creates a new object from the given data, handling CamelCased columns.
        Column mapping can be overriden using `cls.IMPORT_SOURCES`.
        Default values can be specified as **kwargs.
        """
        sheet_name = cls.IMPORT_SOURCES[src_idx]['src']
        mapping = cls.IMPORT_SOURCES[src_idx]['map']
        kernel_keys = set()

        fields = {
            f.name: f
            for f in cls._meta.fields
        }

        # Detect a 2nd pass when we should update a row rather than insert it
        if src_idx > 0:
            current_keys = set(mapping.keys())
            initial_insert_keys = set(cls.IMPORT_SOURCES[0]['map'].keys())

            kernel_keys = initial_insert_keys & current_keys
            extra_keys = current_keys - initial_insert_keys

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
                    try:
                        val = getattr(type(field.choices[0][0]),
                                      utils.str_to_constant_name(val))
                    except AttributeError:
                        logger.error("Invalid value %s for field %s", val, field)
                        raise
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

        for field, column in mapping.items():
            # the "column" can in fact be a tuple of (related field, input column)
            rel_field = None
            if isinstance(column, (tuple)):
                # get the foreign relation by a non-pk field
                rel_field, column = column

            try:
                if isinstance(column, list):
                    # concatenate several columns into one field
                    val = ''.join([str(data[c]) for c in column])
                else:
                    val = data[column]
            except KeyError:
                logger.error("Column %s not found in sheet %s", column, sheet_name)
                raise
            else:
                try:
                    _assign(field, val, rel_field)
                except ObjectDoesNotExist as e:
                    logger.warning(
                        "Error while assigning {}.{}={}, rel_field: {} ({})".format(
                            cls.__name__, field, val, rel_field, e))
                    return

        # if we have kernel_keys then identify an object already in db and update it
        if kernel_keys:
            try:
                identity_values = {k: values[k] for k in kernel_keys}
                obj = cls.objects.get(**identity_values)
                [ setattr(obj, k, values[k]) for k in values if k in extra_keys ]
            except (KeyError, ObjectDoesNotExist) as e:
                logger.warning("Error while grabbing {} instance with identity: {}".format(
                    cls.__name__, identity_values
                ))
                return
            return obj
        # otherwise create a new row
        else:
            return cls(**values)
