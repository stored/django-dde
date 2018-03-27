import pickle
import logging

from celery.task import task

from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.mail import send_mail

from .exceptions import ExporterException

logger = logging.getLogger(__name__)


@task(bind=True)
def task_process(self, exporter_id):
    """ After the creation of the Expoter model, this will be called to start the processing of the tasks.
    It separates the queryset in chunks for assync processing, then calls the chunk processing task """
    from .models import Exporter

    logger.info(f'[#{exporter_id}] Started exporting')

    exporter = Exporter.objects.get(pk=exporter_id)

    exporter.set_status(Exporter.STATUS_CHOICES.processing)

    Model = exporter.content_type.model_class()

    queryset = Model.objects.all()
    queryset.query = pickle.loads(exporter.query.file.read())

    chunk_list = Exporter.objects.create_chunks_from_exporter(exporter, queryset)

    logger.info(f'[#{exporter_id}] {queryset.query}')

    for chunk in chunk_list:
        task_process_chunk.delay(chunk.pk)
        logger.info(f'[#{exporter_id}] Start processing chunk page {chunk.page}')

    exporter.set_status(Exporter.STATUS_CHOICES.processing)

    logger.info(f'[#{exporter_id}] Ended processing')


@task(bind=True)
def task_process_chunk(self, chunk_id):
    """ Proccess the chunk from the exporter. """
    from .models import ExporterChunk

    # Fetch the Chunk model and separates the Exporter Model, also init processing for both
    exporter_chunk = ExporterChunk.objects.get(pk=chunk_id)
    exporter = exporter_chunk.exporter

    logger.info(f'[#{exporter.id}] Start processing chunk #{exporter_chunk.page}')

    exporter_chunk.set_status(ExporterChunk.STATUS_CHOICES.processing)

    Model = exporter.content_type.model_class()
    queryset = Model.objects.all()
    queryset.query = pickle.loads(exporter.query.file.read())

    # Get the current page
    paginator = Paginator(queryset, exporter.limit_per_task)
    page_queryset = paginator.page(exporter_chunk.page)

    path_name = f'reports/{exporter.uuid}/{exporter.uuid}-{exporter_chunk.page}.csv'

    try:
        ExporterChunk.objects.export(
            exporter_chunk,
            page_queryset,
            path_name,
            exporter.attrs
        )

        exporter_chunk.set_status(exporter_chunk.STATUS_CHOICES.success)

        logger.info(f'[#{exporter.id}] Ended processing chunk #{exporter_chunk.page}')

    except ExporterException as error:
        exporter_chunk.set_status(exporter_chunk.STATUS_CHOICES.error)
        logger.error(error)


@task(bind=True)
def task_update_exporter_status(self):
    """ Checks periodicaly if any exposter has completed. If it is then calls the finish_exporter task """
    from .models import Exporter

    # periodic_task
    logger.info('Start checking exporters status')
    exporters = Exporter.objects.filter(status=Exporter.STATUS_CHOICES.processing)

    for exporter in exporters:

        if exporter.chunks_is_successful and exporter.is_pending:
            task_finish_exporter.delay(exporter.id)
            logger.info(f'[#{exporter.id}] Finish completed')

        elif exporter.has_chunk_errors:
            exporter.set_status(Exporter.STATUS_CHOICES.error)
            logger.error(f'[#{exporter.id}] Has chunk errors')

    logger.info('Ended checking exporter status')


@task(bind=True)
def task_finish_exporter(self, exporter_id):
    """ Combines the chunk files in one big file and then saves """
    from .models import Exporter

    exporter = Exporter.objects.get(pk=exporter_id)

    logger.info('f[{exporter.id}] Finishing')

    now = timezone.now()

    path_name = 'reports/{date}-{uuid}.csv'.format(
        date=now.strftime('%Y-%m-%d_%H.%M.%S'),
        uuid=exporter.uuid
    )

    try:
        Exporter.objects.join_files(exporter, path_name)
        exporter.set_status(Exporter.STATUS_CHOICES.done)

        logger.info(f'[#{exporter.id}] Finish successful')

        task_exporter_send_email.delay(exporter_id)

    except ExporterException as error:
        exporter.set_status(exporter.STATUS_CHOICES.error)
        logger.error(error)


@task(bind=True)
def task_exporter_send_email(self, exporter_id):
    """ Sends a email containg the exporter file url to user """
    from .models import Exporter

    exporter = Exporter.objects.get(pk=exporter_id)
    from_email = getattr(settings, 'EXPORTER_FROM_EMAIL', [])

    if not from_email:
        logger.debug(f'[#{exporter.id}] EXPORTER_FROM_MAIL or email not set.')
        return

    send_mail(
        subject="Seu arquivo foi exportado com sucesso!",
        message=default_storage.url(str(exporter.file)),
        from_email=from_email,
        recipient_list=[exporter.email],
        fail_silently=True
    )

    logger.info(f'[#{exporter.id}] Email sent successful')
