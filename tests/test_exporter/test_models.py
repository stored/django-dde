import os
import glob
import pickle
import pytest
import shutil
import json

from autofixture import AutoFixture

from django.contrib.contenttypes.models import ContentType

from exporter.models import Exporter, ExporterChunk


pytestmark = pytest.mark.django_db


def test_create_exporter(users_queryset):
    exporter = Exporter.objects.create_exporter(users_queryset, "teste@teste.com.br", {
        "id": "ID",
        "name": "NOME",
        "email": "EMAIL"
    }, limit_per_task=1)

    assert exporter.id
    assert exporter.uuid

    assert exporter.query
    assert exporter.limit_per_task == 1
    assert exporter.total == 10
    assert exporter.email == 'teste@teste.com.br'
    assert exporter.status == Exporter.STATUS_CHOICES.created

    assert str(pickle.loads(exporter.query.file.read())) == str(users_queryset.query)


def test_create_chunks(users_queryset):
    exporter = Exporter.objects.create(
        content_type=ContentType.objects.get_for_model(users_queryset.model),
        email="teste@teste.com.br",
        attrs=json.dumps({
            "id": "ID",
            "name": "NOME",
            "email": "EMAIL"
        }),
        limit_per_task=1,
        total=users_queryset.count(),
    )

    Exporter.objects.create_chunks_from_exporter(exporter, users_queryset)

    assert exporter.chunks.count() == 10
    assert exporter.chunks.filter(status=ExporterChunk.STATUS_CHOICES.created).count() == 10


def test_set_status(exporter):
    exporter.set_status(Exporter.STATUS_CHOICES.processing)
    assert exporter.status == Exporter.STATUS_CHOICES.processing


def test_exporter_is_pending(exporter):
    exporter.set_status(Exporter.STATUS_CHOICES.processing)
    assert exporter.is_pending


def test_chunk_set_status(exporter):
    chunk = AutoFixture(ExporterChunk, field_values={'exporter': exporter}).create_one()

    chunk.set_status(ExporterChunk.STATUS_CHOICES.success)

    assert chunk.status == ExporterChunk.STATUS_CHOICES.success


def test_chunks_is_successful(exporter):
    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.success,
        'exporter': exporter
    }).create(2)

    assert exporter.chunks_is_successful


def test_chunks_is_successful_is_processing_results(users_queryset, exporter):
    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.success,
        'exporter': exporter
    }).create(2)

    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.processing,
        'exporter': exporter
    }).create_one()

    assert not exporter.chunks_is_successful


def test_chunks_is_successful_is_created_results(users_queryset, exporter):
    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.success,
        'exporter': exporter
    }).create(2)

    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.created,
        'exporter': exporter
    }).create_one()

    assert not exporter.chunks_is_successful


def test_chunks_is_successful_is_error_results(users_queryset, exporter):
    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.success,
        'exporter': exporter
    }).create(2)

    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.error,
        'exporter': exporter
    }).create_one()

    assert not exporter.chunks_is_successful


def test_chunk_has_errors(users_queryset, exporter):
    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.success,
        'exporter': exporter
    }).create(2)

    AutoFixture(ExporterChunk, field_values={
        'status': ExporterChunk.STATUS_CHOICES.error,
        'exporter': exporter
    }).create_one()

    assert exporter.has_chunk_errors


def test_exporter_is_done(exporter):
    exporter.set_status(Exporter.STATUS_CHOICES.done)
    assert exporter.is_done


def teardown_module(module):
    directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
    for item in glob.iglob(os.path.join(directory, '*.pkl')):
        os.remove(item)

    shutil.rmtree(os.path.join(directory, 'reports'), ignore_errors=True)
