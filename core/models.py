from django.db import models
from django.contrib.auth.models import AbstractUser
from oauth2_provider.models import AccessToken, Application
from django.utils import timezone


class User(AbstractUser):
    has_setup = models.BooleanField(default=False)
    verifier = models.CharField(max_length=256, null=True)

    class Meta:
        pass


class TemporaryToken(models.Model):
    identifier = models.CharField(max_length=256)
    token = models.ForeignKey(AccessToken, on_delete=models.CASCADE, null=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True)
    approved = models.BooleanField(default=False)

    error_message = models.CharField(max_length=300, null=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        pass
    # Create your models here.
