from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


@python_2_unicode_compatible
class TwitterAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='twitter'
    )

    username = models.CharField(max_length=140, null=True)
    uid = models.CharField(max_length=60, null=True)

    name = models.TextField(max_length=300, null=True)
    verified = models.BooleanField(null=True)
    profile_image_url_https = models.CharField(max_length=300, null=True)
    description = models.TextField(max_length=600, null=True, blank=True)
    updated = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        verbose_name = _('twitter account')
        verbose_name_plural = _('twitter accounts')

    def __str__(self):
        return self.username


@python_2_unicode_compatible
class OAuth2AccessToken(models.Model):
    account = models.OneToOneField(TwitterAccount, on_delete=models.CASCADE)
    token = models.TextField(
        verbose_name=_('token'),
        help_text=_(
            'access token (OAuth2)'))
    token_secret = models.TextField(
        blank=True,
        verbose_name=_('token secret'),
        help_text=_(
            'refresh token (OAuth2)'))
    expires_at = models.DateTimeField(blank=True, null=True,
                                      verbose_name=_('expires at'))

    class Meta:
        verbose_name = _('Twitter oauth2 token')
        verbose_name_plural = _('Twitter oauth2 tokens')

    def __str__(self):
        return self.token


class TwitterTemporaryToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_token = models.TextField()
    oauth_token = models.CharField(max_length=255, null=True)


class LiveConfiguration(models.Model):
    account = models.OneToOneField(TwitterAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='configuration')

    active = models.BooleanField(default=False)
    update_status_active = models.BooleanField(default=False)


class UsernameConfiguration(models.Model):
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    POSITIONING_CHOICES = (
        (BEFORE, "Before"),
        (AFTER, "After")
    )

    config = models.OneToOneField(LiveConfiguration, on_delete=models.CASCADE)
    live_text = models.TextField(max_length=30, null=True)
    positioning = models.CharField(max_length=10, choices=POSITIONING_CHOICES, default=BEFORE)

    active = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)


class BioConfiguration(models.Model):
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    POSITIONING_CHOICES = (
        (BEFORE, "Before"),
        (AFTER, "After")
    )

    config = models.OneToOneField(LiveConfiguration, on_delete=models.CASCADE)
    live_text = models.TextField(max_length=30, null=True)
    positioning = models.CharField(max_length=10, choices=POSITIONING_CHOICES, default=BEFORE)

    active = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=TwitterAccount)
def account_created(sender, instance, created, *args, **kwargs):
    if created:
        parent_config = LiveConfiguration.objects.create(account=instance, user=instance.user)
        parent_config.save()
        username_config = UsernameConfiguration.objects.create(config=parent_config)
        bio_config = BioConfiguration.objects.create(config=parent_config)
        username_config.save()
        bio_config.save()
