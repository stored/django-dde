# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-09 08:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exporter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('email', models.EmailField(max_length=254)),
                ('query', models.FileField(blank=True, default=None, null=True, upload_to='')),
                ('attrs', jsonfield.fields.JSONField(blank=True, default=None, null=True)),
                ('limit_per_task', models.IntegerField(default=100)),
                ('total', models.IntegerField(editable=False)),
                ('file', models.FileField(blank=True, default=None, null=True, upload_to='')),
                ('status', models.CharField(choices=[('created', 'created'), ('processing', 'processing'), ('done', 'done'), ('error', 'error')], default='created', max_length=16)),
                ('done_at', model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['done', 'error']))),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExporterChunk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('page', models.IntegerField()),
                ('file', models.FileField(blank=True, default=None, null=True, upload_to='')),
                ('status', models.CharField(choices=[('created', 'created'), ('processing', 'processing'), ('success', 'success'), ('error', 'error')], default='created', max_length=16)),
                ('done_at', model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['error', 'success']))),
                ('exporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='exporter.Exporter')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
