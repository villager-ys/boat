from django.db import models


# Create your models here.

class Inventory(models.Model):
    GROUP_ENUM = (
        (1, "master"),
        (2, "worker"),
        (3, "etcd"),
        (4, "certs"),
        (5, "keepalived"),
        (6, "k8s-harbor"),
    )
    host = models.CharField(max_length=15)
    port = models.CharField(max_length=5)
    user = models.CharField(max_length=10)
    password = models.CharField(max_length=14, blank=True, null=True)
    group = models.PositiveIntegerField(blank=True, null=True, choices=GROUP_ENUM)
