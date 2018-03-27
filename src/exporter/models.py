from uuid import uuid4

from django.core.files.storage import default_storage
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

import jsonfield

from model_utils.models import TimeStampedModel
from model_utils.choices import Choices
from model_utils.fields import MonitorField

from .managers import ExporterManager, ExporterChunkManager
from .exceptions import ExporterStatusException


class Exporter(TimeStampedModel):
    """ Exporter model handles the initial creation of the exportation. All the info needed for the exportation comes
    from here  """

    STATUS_CHOICES = Choices(
        ("created", _("created")),
        ("processing", _("processing")),
        ("done", _("done")),
        ("error", _("error"))
    )

    uuid = models.UUIDField(default=uuid4)
    email = models.EmailField()
    content_type = models.ForeignKey(ContentType)
    query = models.FileField(blank=True, null=True, default=None, storage=default_storage)
    attrs = jsonfield.JSONField(blank=True, null=True, default=None)
    limit_per_task = models.IntegerField(default=100)
    total = models.IntegerField(editable=False)
    file = models.FileField(blank=True, null=True, default=None, storage=default_storage)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_CHOICES.created)
    done_at = MonitorField(monitor='status', when=['done', 'error'], default=None, null=True)

    objects = ExporterManager()

    def set_status(self, status):
        """ Sets the status to one of the status choices """
        if status not in self.STATUS_CHOICES:
            raise ExporterStatusException("Invalid status.")

        self.status = status
        self.save()

    @property
    def chunks_is_successful(self):
        """ Check if its chunks are completed succesful """
        return self.chunks.filter(status=ExporterChunk.STATUS_CHOICES.success).count() == self.chunks.all().count()

    @property
    def has_chunk_errors(self):
        """ Check if any of the created chunks have returned errors """
        return self.chunks.filter(status=ExporterChunk.STATUS_CHOICES.error).exists()

    @property
    def is_pending(self):
        """ Check if it is pending """
        return self.status == self.STATUS_CHOICES.processing

    @property
    def is_done(self):
        return self.status == self.STATUS_CHOICES.done


class ExporterChunk(TimeStampedModel):
    STATUS_CHOICES = Choices(
        ("created", _("created")),
        ("processing", _("processing")),
        ("success", _("success")),
        ("error", _("error"))
    )

    exporter = models.ForeignKey(Exporter, related_name="chunks")
    page = models.IntegerField()
    file = models.FileField(blank=True, null=True, default=None, storage=default_storage)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_CHOICES.created)
    done_at = MonitorField(monitor='status', when=['success', 'error'], default=None, null=True)

    objects = ExporterChunkManager()

    def set_status(self, status):
        """ Sets the status to one of the choices """
        if status not in self.STATUS_CHOICES:
            raise ExporterStatusException("Invalid status.")

        self.status = status
        self.save()
