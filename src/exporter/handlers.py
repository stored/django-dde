import csv
import tempfile
import codecs

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .utils import ExporterHelper


def handler_default_storage(exporter, path_name):
    """ Join the file_list (chunked files) into one then saves and return the saved path """
    header = ExporterHelper.get_header(exporter.attrs)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=True, encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=str(';'), quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        f.flush()

        for chunk in exporter.chunks.all():
            with default_storage.open(chunk.file.name) as temp_file:
                reader = csv.reader(codecs.iterdecode(temp_file, 'utf-8'))
                for row in reader:
                    writer.writerow(row[0].split(';'))
                    f.flush()

        # TODO search for better solution
        # need to be a binary file, but csv.writerow can't write binary, try user DictWriter subclass
        readble_file = open(f.name, 'rb').read()

        exporter.file.save(path_name, ContentFile(readble_file))

    return exporter


def handle_s3():
    pass
