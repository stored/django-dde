import json

from functools import reduce
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime


class ExporterHelper:
    """ Helper methods - This class focus on handling the files generated by the chunks/exporter """
    # TODO Refactoring is need, some code is legacy

    @classmethod
    def get_header(cls, columns):
        """ Separates the header from the json attrs"""
        columns = json.loads(columns)
        return [attr for attr in columns]

    @classmethod
    def get_row(cls, obj, attrs):
        """ Generates a csv row based on the attrs and received object """
        attrs = json.loads(attrs)
        data = cls._extract_data(obj, attrs)
        row = [data.get(attr) for attr in attrs]
        return cls._format_row(row)

    @classmethod
    def _extract_data(cls, obj, attrs):
        """ Extract data of the object based on the selected attrs """
        data = {}

        for key, attr in attrs.items():
            default = attr[1] if isinstance(attr, list) else None
            data.update({key: cls._extract_data_by_attr(obj, attr, default)})

        return data

    @classmethod
    def _extract_data_by_attr(cls, obj, attr, default=None):
        """ Deep searchs for the attr in the model then returns it."""
        try:
            value = cls._deepgetattr(obj, attr, default)
        except Exception as error:
            value = None
        return value

    @classmethod
    def _format_row(cls, row):
        """ Formats row for csv reading """
        _row = []
        for item in row:
            if isinstance(item, Decimal):
                item = float(item.quantize(Decimal('.01'), ROUND_HALF_UP))
            if isinstance(item, (datetime, date)):
                item = item.isoformat()
            if isinstance(item, str):
                item = str(item).replace('\n', '\r\n')
            if isinstance(item, str):
                item = item.replace('\n', '\r\n')
            _row.append(item)
        return _row

    @classmethod
    def _deepgetattr(cls, obj, attr, default=None):
        """ Deep searchs for the property on the model if exists returns it, if don't, assumes a default value """

        def getattr_(o, k):
            if hasattr(o, 'has_key'):
                v = o.get(k, default)

            #  TODO: Add tratative for int values
            else:
                v = getattr(o, k, default)

            return v() if callable(v) else v

        return reduce(getattr_, attr.split('.'), obj)
