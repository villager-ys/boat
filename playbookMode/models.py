import uuid
from django.db import models
from django.conf import settings


# Create your models here.
class Playbook(models.Model):
    playbook_name = models.CharField(max_length=15)
    playbook_content = models.FileField(upload_to='.')
    playbook_description = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-create_time']
