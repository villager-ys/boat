import uuid
from django.db import models
from django.conf import settings


# Create your models here.
class PlaybookDetail(models.Model):
    playbook_name = models.CharField(max_length=15)
    playbook_content = models.FileField(upload_to='%s/conf/media' % settings.BASE_DIR)
    playbook_detail = models.TextField()
