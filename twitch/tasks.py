import datetime
import pytz
import logging
import requests

from django.conf import settings

from twitch.models import TwitchAccount, TwitchSubscription
from .utils import get_absolute_uri
from twitch import app_settings
from liveontwitch.celery import app

# from celery import shared_task
from core import errors

logger = logging.getLogger(__name__)


@app.task
def twitch_subscribe_webhook(uid, method="subscribe"):
    """
    Creates the subscription for a twitch account when a user signs up
    :param uid: twitch uid
    :param method: whether to unsubscribe or subscribe
    :return:
    """
    try:
        account = TwitchAccount.objects.get(uid=uid)
    except TwitchAccount.DoesNotExist:
        logger.error("NO_ACCOUNT_FOUND")

    else:
        if hasattr(account, 'twitchsubscription'):
            subscription = account.twitchsubscription
        else:
            subscription = TwitchSubscription.objects.create(
                account=account,
                confirmed=False
            )

        headers = {
            "Client-ID": settings.TWITCH_AUTH_CLIENT_ID,
        }
        payload = {
            "hub.callback": get_absolute_uri(settings.TWITCH_SUBSCRIPTION_CALLBACK_URL),
            "hub.mode": method,
            "hub.topic": f"https://api.twitch.tv/helix/streams?user_id={uid}",
            "hub.lease_seconds": 864000,
            "hub.secret": settings.TWITCH_SUBSCRIPTION_KEY
        }
        r = requests.post(app_settings.SUBSCRIPTION_URL, data=payload, headers=headers)
        if r.status_code == 202:
            logger.info(f"Requested Sub: {account.user.username}")
            subscription.confirmed = False
        else:
            logger.error(f"{errors.TWITCH_HUB_SUBSCRIPTION_ERROR}:{r.text}")
            subscription.error_message = f"SUBSCRIBE_POST:{r.text}"
            subscription.confirmed = False

        subscription.verifier = None
        subscription.save()

