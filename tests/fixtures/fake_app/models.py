from django.db import models


class FakeModel(models.Model):

    name = models.CharField('name', max_length=100)
    email = models.EmailField()
    info_1 = models.CharField(max_length=40)
    info_2 = models.DateTimeField()

    class Meta:
        ordering = ['id']
