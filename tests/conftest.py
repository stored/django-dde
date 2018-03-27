import pytest

from autofixture import AutoFixture

from tests.fixtures.fake_app.models import FakeModel
from exporter.models import Exporter


@pytest.fixture(name="users")
def fixture_users():
    return AutoFixture(FakeModel).create(10)


@pytest.fixture(name="users_queryset")
def fixture_users_queryset(users):
    return FakeModel.objects.all()


@pytest.fixture(name="exporter")
def fixture_exporter(users_queryset):
    return Exporter.objects.create_exporter(users_queryset, "teste@teste.com.br", {
        "id": "ID",
        "name": "NOME",
        "email": "EMAIL"
    }, 1)
