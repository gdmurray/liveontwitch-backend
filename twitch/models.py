from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .fields import JSONField
from django.utils import timezone


@python_2_unicode_compatible
class TwitchAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='twitch'
    )

    uid = models.CharField(verbose_name=_('uid'), max_length=139, unique=True)
    extra_data = JSONField(verbose_name=_('extra data'), default=dict)

    partnered = models.BooleanField(default=False)
    email = models.CharField(max_length=160, null=True)
    logo = models.CharField(max_length=300, null=True)

    # display_name = models.CharField(max_length=120, null=True)
    # name = models.CharField(max_length=120, null=True)

    class Meta:
        verbose_name = _('twitch account')
        verbose_name_plural = _('twitch accounts')

    def __str__(self):
        return self.user.username

    def get_profile_url(self):
        return 'https://twitch.tv/' + self.account.extra_data.get('name')

    def get_avatar_url(self):
        return self.account.extra_data.get('logo')


@python_2_unicode_compatible
class OAuth2AccessToken(models.Model):
    account = models.OneToOneField(TwitchAccount, on_delete=models.CASCADE, null=True)
    token = models.TextField(
        verbose_name=_('token'),
        help_text=_(
            'access token (OAuth2)'))
    token_secret = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('token secret'),
        help_text=_(
            'refresh token (OAuth2)'))
    expires_at = models.DateTimeField(blank=True, null=True,
                                      verbose_name=_('expires at'))
    application_token = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Twitch oauth2 token')
        verbose_name_plural = _('Twitch oauth2 tokens')

    def __str__(self):
        return self.token


class TwitchSubscription(models.Model):
    account = models.OneToOneField(TwitchAccount, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)

    subscription_date = models.DateTimeField(null=True)
    expiry = models.DateTimeField(null=True)
    expiry_seconds = models.IntegerField(default=864000)

    confirmed = models.BooleanField(default=False)
    verifier = models.CharField(max_length=256, null=True, blank=True)
    error_message = models.CharField(max_length=300, null=True, blank=True)


class TwitchEvent(models.Model):
    """
    Persist events to see if the system received
    """
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    status_choices = (
        (ONLINE, "Online"),
        (OFFLINE, "Offline")
    )

    subscription = models.ForeignKey(TwitchSubscription, on_delete=models.CASCADE, null=True)
    account = models.ForeignKey(TwitchAccount, on_delete=models.CASCADE, null=True)
    event_id = models.CharField(max_length=256, null=True, blank=True)
    action = models.CharField(choices=status_choices, max_length=15)
    created = models.DateTimeField(auto_now_add=timezone.now)
