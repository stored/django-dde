import pytest

from autofixture import AutoFixture

from empiricus_api.accounts.models import User
from empiricus_api.exporter.models import Exporter, ExporterChunk


@pytest.fixture(name="users")
def fixture_users():
    return AutoFixture(User).create(10)


@pytest.fixture(name="users_queryset")
def fixture_users_queryset(users):
    return User.objects.all()


@pytest.fixture(name="exporter")
def fixture_exporter(users_queryset):
    return Exporter.objects.create_exporter(users_queryset, "teste@teste.com.br", {
        "id": "ID",
        "name": "NOME",
        "email": "EMAIL"
    }, 1)
