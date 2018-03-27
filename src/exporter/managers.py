import csv
import json
import pickle
import tempfile
import codecs

from django.db import models, transaction
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .utils import ExporterHelper
from .tasks import task_process


class ExporterManager(models.Manager):

    def create_exporter(self, queryset, email, attrs, limit_per_task=100):
        Model = self.model

        content = pickle.dumps(queryset.query)
        query_file = ContentFile(content)

        obj = Model.objects.create(
            content_type=ContentType.objects.get_for_model(queryset.model),
            email=email,
            attrs=json.dumps(attrs),
            limit_per_task=limit_per_task,
            total=queryset.count(),
        )

        obj.query.save(f'{obj.uuid}_queryset.pkl', query_file)

        task_process.delay(obj.id)

        return obj

    def create_chunks_from_exporter(self, exporter, queryset):
        from .models import ExporterChunk

        chunk_list = []
        paginator = Paginator(queryset, exporter.limit_per_task)

        with transaction.atomic():
            for page in paginator.page_range:
                exporter_chunk = ExporterChunk.objects.create(exporter=exporter, page=page)
                chunk_list.append(exporter_chunk)

        return chunk_list

    def join_files(cls, exporter, path_name):
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


class ExporterChunkManager(models.Manager):

    def export(self, chunk, page_queryset, path_name, columns):
        """ Exports a CSV file containing the item_list """
        rows = []
        for obj in page_queryset:
            rows.append(ExporterHelper.get_row(obj, columns))

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=True, encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=str(';'), quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                writer.writerow(row)
                f.flush()

            # TODO search for better solution
            # need to be a binary file, but csv.writerow can't write binary, try user DictWriter subclass
            readble_file = open(f.name, 'rb').read()

            chunk.file.save(path_name, ContentFile(readble_file))

        return chunk
