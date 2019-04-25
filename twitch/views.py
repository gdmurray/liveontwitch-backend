import logging
from datetime import timedelta
import datetime
import pytz
import urllib.parse as urlparse
import hashlib
import hmac
import base64
import pickle

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from oauth2_provider.models import Application, AccessToken
from oauthlib import common
from django.utils import timezone
from rest_framework.parsers import FormParser
from rest_framework.decorators import parser_classes

from twitch import app_settings
from twitch.utils import build_url, get_absolute_uri
from core.models import TemporaryToken
from twitch.models import TwitchEvent, TwitchAccount, TwitchSubscription
from .parsers import TwitchPostParser

logger = logging.getLogger(__name__)


def connect(request):
    logger.info("Requesting Authentication")
    identifier = request.GET.get('identifier', None)
    application = request.GET.get('application', None)
    token = TemporaryToken.objects.filter(identifier=identifier)
    if token.count() > 0:
        logger.warning("Identifier used before")
        return JsonResponse(status=403, data={"message": "identifier has been used"})

    try:
        oauth_application = Application.objects.get(client_id=application)
        token = TemporaryToken.objects.create(identifier=identifier, application=oauth_application)
        token.save()
        authorize_url = app_settings.AUTHORIZE_URL
        params = {
            'redirect_uri': get_absolute_uri(app_settings.CALLBACK_URL),
            'state': identifier
        }
        return JsonResponse(status=200, data={"auth_url": build_url(authorize_url, params)})
    except Application.DoesNotExist:
        print("Do some error shit, no application found")
    # return HttpResponseRedirect(build_url(authorize_url, params))


def login(request):
    redirect_to = request.GET.get('next', app_settings.REDIRECT_URI)
    print("redirect to ", redirect_to)
    if request.user.is_authenticated:
        return HttpResponseRedirect(redirect_to)
    authorize_url = app_settings.AUTHORIZE_URL
    params = {
        'redirect_uri': get_absolute_uri(app_settings.CALLBACK_URL)
    }
    verifier = get_random_string()
    request.session['state'] = (redirect_to, verifier)
    params['state'] = verifier
    print("params ", params)
    return HttpResponseRedirect(build_url(authorize_url, params))


def callback(request):
    # Could not authorize twitch app
    if 'error' in request.GET:
        # todo: handle appropriately
        error_message = _('You denied access to your Twitch account') \
            if request.GET['error'] == 'access_denied' else _('Error while authentication via Twitch API')
        messages.error(request, error_message)
        logger.error('[Twitch Auth] %s: %s' % (request.META['REMOTE_ADDR'], request.GET['error_description']))
        return HttpResponseRedirect('/')

    # get redirection url
    # todo:  make dynamic or username state based => setup/home/etc
    redirect_to = settings.FRONTEND_URL + settings.FRONTEND_CALLBACK

    code = request.GET['code']
    state = request.GET['state']
    logger.error(f"{code}, {state}")

    # if user is already logged in, redirect to that url
    # if request.user.is_authenticated:
    #    return HttpResponseRedirect(redirect_to)

    # authenticate with backend
    user = authenticate(request, code=request.GET['code'])
    if user and user.is_active:
        # auth_login(request, user)
        # todo: create oauth2 token
        try:
            expires = timezone.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
            temporary_token = TemporaryToken.objects.get(identifier=state)
            application = temporary_token.application
            access_token = AccessToken(
                user=user,
                scope='',
                expires=expires,
                token=common.generate_token(),
                application=application
            )
            access_token.save()
            temporary_token.token = access_token
            temporary_token.approved = True
            temporary_token.save()

        except TemporaryToken.DoesNotExist:
            print("Yo we couldnt find this")
        # messages.success(request, _('You successfully logged in'))
        return HttpResponseRedirect(redirect_to)
    else:
        print("not an existing user... complete setup")
        # messages.error(request, _('Cannot authenticate you'))
        return HttpResponseRedirect('/')


@csrf_protect
def logout(request):
    auth_logout(request)
    messages.success(request, _('You successfully logged out'))
    return HttpResponseRedirect('/')


def fetch_token(request):
    identifier = request.GET.get('identifier', None)
    application = request.GET.get('application', None)
    print(identifier, application)
    try:
        temp = TemporaryToken.objects.get(identifier=identifier, application__client_id=application)
        data = {"token": temp.token.token}
        return JsonResponse(status=200, data=data)
    except TemporaryToken.DoesNotExist:
        # todo: make the message come from the temporary token?
        return JsonResponse(status=404, data={"message": "No Token Pair Found"})


import json


class TwitchSubscriptionEndpoint(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (TwitchPostParser,)

    def get(self, request, *args, **kwargs):
        logger.error("GOT SUBSCRIPTION FROM TWITCH")
        mode = request.GET.get('hub.mode')
        topic = request.GET.get('hub.topic')
        now = datetime.datetime.now(tz=pytz.utc)

        try:
            uid = topic.split("=")[-1]
            subscription = TwitchSubscription.objects.get(account__uid=uid)
        except TwitchSubscription.DoesNotExist:
            logger.error("No Twitch Subscription Found For this User")
            return HttpResponse(status=404)

        if mode == "subscribe":
            challenge = request.GET.get('hub.challenge')
            lease_seconds = int(request.GET.get('hub.lease_seconds'))
            expiry = now + datetime.timedelta(seconds=864000)
            subscription.expiry = expiry
            subscription.expiry_seconds = lease_seconds
            subscription.subscription_date = now
            subscription.confirmed = True
            subscription.verifier = challenge
            subscription.error_message = ''
            subscription.save()

            return HttpResponse(status=200, content=challenge)
        elif mode == "denied":
            reason = request.GET.get('hub.reason')
            subscription.confirmed = False
            subscription.error_message = f"SUBSCRIBE_GET: {reason}"
            subscription.subscription_date = None
            subscription.expiry = None
            subscription.verifier = None
            subscription.save()
            logger.error(f"SUBSCRIBE_GET: {reason}")
            return HttpResponse(status=400)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        link_header = request.headers['Link']
        parsed = urlparse.urlparse(link_header.replace('<', '').replace('>', '').split(',')[-1])
        header_user_id = urlparse.parse_qs(parsed.query)['user_id'][0]
        try:
            twitch_account = TwitchAccount.objects.get(uid=header_user_id)
            twitch_sub = TwitchSubscription.objects.get(account=twitch_account)
        except TwitchAccount.DoesNotExist:
            logger.error(f"No Twitch Account with ID: {header_user_id}")
            return HttpResponse(200)
        except TwitchSubscription.DoesNotExist:
            logger.error(f"No Twitch Subscription for ID: {header_user_id}")
            return HttpResponse(200)
        event_id = request.headers['Twitch-Notification-Id']
        signature = request.headers['X-Hub-Signature']
        my_sig = "sha256=" + hmac.new(settings.TWITCH_SUBSCRIPTION_KEY.encode('utf-8'),
                                      msg=request.raw_body.encode('utf-8'),
                                      digestmod=hashlib.sha256).hexdigest()

        if signature != my_sig:
            logger.error("INVALID SIGNATURE")
            return HttpResponse(status=403)

        event = TwitchEvent(subscription=twitch_sub, account=twitch_account, event_id=event_id)
        data = request.data['data']
        if len(data) > 0:
            # TODO: Parse Body For More Informative User Data
            event = data[0]
            if event['type'] == "live":
                event.action = TwitchEvent.ONLINE
        else:
            event.action = TwitchEvent.OFFLINE
        event.save()

        return HttpResponse(status=200)
