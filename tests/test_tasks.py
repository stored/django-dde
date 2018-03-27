import pytest

from autofixture import AutoFixture
from .generators import CustomDocumentGenerator

from django.core import mail
from django.core.files.storage import default_storage

from empiricus_api.accounts.models import User
from empiricus_api.exporter.models import Exporter, ExporterChunk
from empiricus_api.exporter.tasks import (
    task_process, task_update_exporter_status, task_exporter_send_email
)


pytestmark = pytest.mark.django_db


def test_task_creation_and_proccess(exporter):
    assert exporter.status == Exporter.STATUS_CHOICES.created

    exporter.refresh_from_db()

    assert exporter.is_pending
    assert exporter.chunks_is_successful


def test_task_update_status(exporter):
    assert exporter.status == Exporter.STATUS_CHOICES.created

    exporter.refresh_from_db()

    assert exporter.is_pending
    assert exporter.chunks_is_successful

    task_update_exporter_status()

    exporter.refresh_from_db()

    assert exporter.file
    assert exporter.is_done


def test_sendmail(exporter):
    assert exporter.status == Exporter.STATUS_CHOICES.created

    exporter.refresh_from_db()

    assert exporter.is_pending
    assert exporter.chunks_is_successful

    task_update_exporter_status()

    exporter.refresh_from_db()

    assert exporter.file
    assert exporter.is_done

    assert len(mail.outbox) == 1

    outbox = mail.outbox[0]

    assert outbox.subject == 'Seu arquivo foi exportado com sucesso!'
    assert outbox.from_email == "teste@teste.com.br"
    assert outbox.to == ["teste@teste.com.br"]
    assert outbox.body == default_storage.url(str(exporter.file))


def test_full_creation(users_queryset):
    assert users_queryset.count() == 10

    exporter = Exporter.objects.create_exporter(users_queryset, "teste@teste.com.br", {
        "id": "ID",
        "name": "NOME",
        "email": "EMAIL"
    }, 1)

    assert exporter.uuid
    assert exporter.query
    assert exporter.attrs
    assert exporter.email == "teste@teste.com.br"
    assert exporter.limit_per_task == 1
    assert exporter.total == 10

    exporter.refresh_from_db()

    assert exporter.is_pending
    assert exporter.chunks_is_successful

    task_update_exporter_status()

    exporter.refresh_from_db()

    assert exporter.file
    assert exporter.is_done

    assert len(mail.outbox) == 1

    outbox = mail.outbox[0]

    assert outbox.subject == 'Seu arquivo foi exportado com sucesso!'
    assert outbox.from_email == "teste@teste.com.br"
    assert outbox.to == ["teste@teste.com.br"]
    assert outbox.body == default_storage.url(str(exporter.file))


def test_full_creation_single_user():
    AutoFixture(User).create_one()

    users_queryset = User.objects.all()

    assert users_queryset.count() == 1

    exporter = Exporter.objects.create_exporter(users_queryset, "teste@teste.com.br", {
        "id": "ID",
        "name": "NOME",
        "email": "EMAIL"
    }, 10)

    assert exporter.uuid
    assert exporter.query
    assert exporter.attrs
    assert exporter.email == "teste@teste.com.br"
    assert exporter.limit_per_task == 10
    assert exporter.total == 1

    exporter.refresh_from_db()

    assert exporter.is_pending
    assert exporter.chunks_is_successful

    task_update_exporter_status()

    exporter.refresh_from_db()

    assert exporter.file
    assert exporter.is_done

    outbox = mail.outbox[0]

    assert outbox.subject == 'Seu arquivo foi exportado com sucesso!'
    assert outbox.from_email == "teste@teste.com.br"
    assert outbox.to == ["teste@teste.com.br"]
    assert outbox.body == default_storage.url(str(exporter.file))


def test_full_creation_with_rest_some_items_on_last_page():
    AutoFixture(User).create(12)

    users_queryset = User.objects.all()

    exporter = Exporter.objects.create_exporter(users_queryset, "teste@teste.com.br", {
        "id": "ID",
        "name": "NOME",
        "email": "EMAIL"
    }, 10)

    assert exporter.uuid
    assert exporter.query
    assert exporter.attrs
    assert exporter.email == "teste@teste.com.br"
    assert exporter.limit_per_task == 10
    assert exporter.total == 12

    exporter.refresh_from_db()

    assert exporter.is_pending
    assert exporter.chunks_is_successful

    task_update_exporter_status()

    exporter.refresh_from_db()

    assert exporter.file
    assert exporter.is_done

    outbox = mail.outbox[0]

    assert outbox.subject == 'Seu arquivo foi exportado com sucesso!'
    assert outbox.from_email == "teste@teste.com.br"
    assert outbox.to == ["teste@teste.com.br"]
    assert outbox.body == default_storage.url(str(exporter.file))


@pytest.mark.skip(reason="only demostration on local environment")
def test_full_creation_massive_test():
    AutoFixture(User, field_values={'document': CustomDocumentGenerator()}).create(10007)

    users_queryset = User.objects.all()

    exporter = Exporter.objects.create_exporter(users_queryset, "teste@teste.com.br", {
        "id": "ID",
        "name": "NOME",
        "email": "EMAIL"
    }, 100)

    assert exporter.uuid
    assert exporter.query
    assert exporter.attrs
    assert exporter.email == "teste@teste.com.br"
    assert exporter.limit_per_task == 100
    assert exporter.total == 10007

    exporter.refresh_from_db()

    assert exporter.is_pending
    assert exporter.chunks_is_successful

    task_update_exporter_status()

    exporter.refresh_from_db()

    assert exporter.file
    assert exporter.is_done

    outbox = mail.outbox[0]

    assert outbox.subject == 'Seu arquivo foi exportado com sucesso!'
    assert outbox.from_email == "teste@teste.com.br"
    assert outbox.to == ["teste@teste.com.br"]
    assert outbox.body == default_storage.url(str(exporter.file))
