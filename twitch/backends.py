import logging

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.urls import reverse

from twitch import app_settings
from twitch.models import OAuth2AccessToken, TwitchAccount
from twitch.utils import get_absolute_uri
from core.models import User
from twitch.tasks import twitch_subscribe_webhook
from .serializers import TwitchAccountInformationSerializer

logger = logging.getLogger(__name__)


class OAuth2Backend(ModelBackend):
    token_url = 'https://api.twitch.tv/kraken/oauth2/token'
    profile_url = 'https://api.twitch.tv/kraken/user'

    # We delegate the responsibility of authentication to the Twitch auth service
    # and only get the access_token from Twitch

    def authenticate(self, request, code=None, *args, **kwargs):
        # Case for Admin-level logins
        if 'username' in kwargs and 'password' in kwargs:
            print("authenticating for admin user")
            username, password = kwargs['username'], kwargs['password']
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
            else:
                if user.is_superuser and user.is_staff:
                    if user.check_password(password):
                        return user
                return None
        else:
            # Regular Twitch Account logins

            if code is None:
                logger.error('Auth code is not provided')
                return None

            resp = requests.post(
                self.token_url,
                data={
                    'client_id': app_settings.CLIENT_ID,
                    'client_secret': app_settings.CLIENT_SECRET,
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': get_absolute_uri(reverse('callback_twitch'))
                })
            try:
                data = resp.json()
            except ValueError:
                logger.error('Twitch auth service returned bad response: %s' % resp.content)
                return None

            if 'access_token' in data:
                token = data['access_token']
            else:
                print("bad response")
                logger.error('Twitch auth service returned bad response: %s' % data)
                return None

            # Fetch or Create User Profile
            user, twitch_account = self.get_user_profile(token)

            try:
                token_obj = OAuth2AccessToken.objects.get(account=twitch_account)
            except OAuth2AccessToken.DoesNotExist:
                token_obj = OAuth2AccessToken()
                token_obj.account = twitch_account
            token_obj.token = token
            token_obj.token_secret = data.get('refresh_token', '')
            token_obj.save()

            return user

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_profile(self, token):
        resp = requests.get(self.profile_url,
                            params={'oauth_token': token, 'client_id': app_settings.CLIENT_ID})
        try:
            profile = resp.json()
        except ValueError:
            logger.error('Twitch profileservice returned bad response: %s' % resp.content)
            return None

        try:
            twitch_account = TwitchAccount.objects.get(uid=profile['_id'])
            user = twitch_account.user
        except TwitchAccount.DoesNotExist:
            twitch_account = TwitchAccount()
            user = get_user_model().objects.create(username=profile['display_name'])
            twitch_account.user = user
            twitch_account.uid = profile['_id']
            twitch_subscribe_webhook.apply_async((profile['_id']))

        user.username = profile['display_name']
        user.email = profile.get('email', user.email)
        twitch_account.extra_data = profile
        twitch_account.save()

        # Serialize additional fields into data
        serializer = TwitchAccountInformationSerializer(twitch_account, profile, partial=True)
        if serializer.is_valid():
            serializer.save()

        user.save()
        return user, twitch_account
