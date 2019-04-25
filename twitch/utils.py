import datetime
import pytz
import json
import requests
import logging

from django.utils.http import urlencode
from django.conf import settings
from rest_framework.exceptions import NotAuthenticated

from twitch import app_settings
from twitch.models import OAuth2AccessToken

logger = logging.getLogger(__name__)


def get_absolute_uri(url):
    """
    Returns an absolute uri for the current application
    :param url:
    :return:
    """
    return app_settings.PROTOCOL + "%s%s" % (settings.SITE_URL, url)


def build_url(url, extra_params):
    """
    Builds the URL for Twitch Auth Request
    :param url: absolute URI
    :param extra_params: url-encoded paramters
    :return:
    """
    params = {
        'client_id': app_settings.CLIENT_ID,
        'scope': app_settings.SCOPE,
        'response_type': 'code'
    }
    params.update(extra_params)
    return "%s?%s" % (url, urlencode(params))


def subscribe_to_stream_change(twitch_id):
    body = {
        "hub.lease_seconds": 864000,
        "hub.mode": "subscribe",
        "hub.topic": f"https://api.twitch.tv/helix/streams?user_id={twitch_id}",
        "hub.callback": get_absolute_uri("/twitch/subscription/callback"),
    }


def verify_headers(request) -> bool:
    """
    Verify authenticity of a Webhook Request
    :param request:
    :return:
    """
    if "X-Hub-Signature" in request.headers:
        signature = request.headers['X-Hub-Signature']


def fetch_new_application_token():
    print("Creating New Application Token")
    now = datetime.datetime.now(tz=pytz.utc)

    # Delete Previous Application Tokens
    OAuth2AccessToken.objects.filter(application_token=True).delete()

    params = {
        "client_id": settings.TWITCH_AUTH_CLIENT_ID,
        "client_secret": settings.TWITCH_AUTH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    r = requests.post(app_settings.ACCESS_TOKEN_URL, data=params)

    # Successful Authentication
    if r.status_code == 200:
        response = json.loads(r.text)
        token = OAuth2AccessToken(
            token=response['access_token'],
            expires_at=now + datetime.timedelta(seconds=int(response['expires_in'])),
            application_token=True
        )
        token.save()
    else:
        logger.error("Could Not Fetch New Token")
        token = None

    return token


def get_application_token():
    """
    Fetches the Twitch Application Access Token
    :return:
    """
    try:
        token = OAuth2AccessToken.objects.get(application_token=True)

        # Check if application token has expired
        if datetime.datetime.now(tz=pytz.utc) >= token.expires_at:
            token = fetch_new_application_token()
        else:
            print("Using Old token")
    except OAuth2AccessToken.DoesNotExist:
        token = fetch_new_application_token()

    return token


def get_subscriptions():
    """
    Returns a List of Current Twitch Subscriptions
    :return:
    """
    token = get_application_token()
    headers = {
        "Authorization": f"Bearer {token.token}"
    }
    r = requests.get(app_settings.SUBSCRIPTION_LIST_URL, headers=headers)

    data = json.loads(r.text)
    return data
