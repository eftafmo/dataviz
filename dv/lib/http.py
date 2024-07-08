import csv
import io

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse


class SetEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return sorted(list(obj))
        return super().default(obj)


class JsonResponse(JsonResponse):
    """
    Like Django's JsonResponse, but serializes "unsafe" data by default
    and sets other defaults.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("safe", False)
        kwargs.setdefault("json_dumps_params", {})
        kwargs["json_dumps_params"].setdefault("indent", 2)

        super(JsonResponse, self).__init__(*args, **kwargs)


class CsvResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to CSV.

    :param data: Input data, either as a list of sequences or of dictionaries.
    :param fieldnames: The field names used in the CSV header.
    :param csv_writer_params: Dict of params passed to the csv writer class.
    """

    def __init__(self, data, fieldnames=None, csv_writer_params=None, **kwargs):
        # TODO: set this as default
        # kwargs.setdefault('content_type', 'text/csv')
        kwargs.setdefault("content_type", "text/plain")
        output = io.StringIO()

        try:
            first = data[0]
        except IndexError:
            pass
        else:
            if csv_writer_params is None:
                csv_writer_params = {}

            if isinstance(first, dict):
                self.write_csv_from_dicts(
                    output, data, fieldnames=fieldnames, **csv_writer_params
                )
            else:
                self.write_csv_from_sequences(
                    output, data, fieldnames=fieldnames, **csv_writer_params
                )

        super().__init__(content=output.getvalue().encode("utf-8"), **kwargs)

    @staticmethod
    def write_csv_from_dicts(stream, data, fieldnames=None, **writer_params):
        if not fieldnames:
            fieldnames = data[0].keys()
        writer = csv.DictWriter(stream, fieldnames=fieldnames, **writer_params)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

    @staticmethod
    def write_csv_from_sequences(stream, data, fieldnames=None, **writer_params):
        writer = csv.writer(stream, **writer_params)
        if fieldnames:
            writer.writerow(fieldnames)
        for item in data:
            writer.writerow(item)
