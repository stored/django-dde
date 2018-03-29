from django.apps import AppConfig
from celery import Celery


app = Celery(__name__)


class FakeApptestConfig(AppConfig):
    name = 'tests.fixtures.fake_app'

    def ready(self):
        app.config_from_object('django.conf:settings', namespace='CELERY')
        app.autodiscover_tasks()
