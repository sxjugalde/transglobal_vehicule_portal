import os

from django.db import models

from utils.models.AuditableModel import AuditableModel


class File(AuditableModel):
    BASE_UPLOAD_FOLDER = "uploads/"

    name = models.CharField(max_length=254, blank=False, unique=True)
    extension = models.CharField(max_length=10)
    file = models.FileField(upload_to=BASE_UPLOAD_FOLDER, blank=False)

    class Meta:
        verbose_name = "file"
        verbose_name_plural = "files"

    def save(self, *args, **kwargs):
        path, file_name = os.path.split(self.file.name)
        base, file_extension = os.path.splitext(file_name)
        self.name = file_name
        self.extension = file_extension
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
