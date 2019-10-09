import uuid
from django.db import models


# Create your models here.
class PlaybookDetail(models.Model):
    playbook_id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4(), editable=False)
    
