import os
import csv
import json
import pickle
import tempfile

from django.db import models, transaction
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import File, ContentFile

from .utils import ExporterHelper


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

        obj.process()

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


class ExporterChunkManager(models.Manager):

    def export(self, chunk, page_queryset, path_name, columns):
        """ Exports a CSV file containing the item_list """
        rows = []
        for obj in page_queryset:
            rows.append(ExporterHelper.get_row(obj, columns))

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False, encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=str(';'))
            for row in rows:
                writer.writerow(row)
                f.flush()

        with open(f.name, 'rb') as f:
            chunk.file.save(path_name, File(f))

        os.remove(f.name)

        return chunk
