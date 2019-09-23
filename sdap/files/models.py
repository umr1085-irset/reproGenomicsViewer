import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User
from django.conf import settings


# Create your models here.
class Folder(models.Model):

    name = models.CharField(max_length=200)
    folder = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_updated_by')

    def __str__(self):
        return self.name


class File(models.Model):

    FILE_TYPE = (
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('CSV', 'Csv'),
        ('PDF', 'Pdf'),
        ('RDATA', 'RDdata'),
        ('EXPRESSION_MATRIX', 'Expression matrix'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField("description", blank=True)
    type = models.CharField(max_length=50, choices=FILE_TYPE, default="TEXT")
    file = models.FileField(upload_to='files/')
    folder = models.ForeignKey(Folder, blank=True, null=True, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_updated_by')

    def __str__(self):
        return self.name

