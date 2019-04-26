import logging
import json
import oauth2 as oauth
from urllib.parse import parse_qsl
import twitter

from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.generics import DestroyAPIView
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from rest_framework.views import APIView

from .models import TwitterTemporaryToken, TwitterAccount, OAuth2AccessToken
from .tasks import fetch_user_info
from .utils import convert
from .serializers import AuthorizedTwitterAccountSerializer, ProfileDetailSerializer, \
    UsernameConfigurationSerializer, BioConfigurationSerializer

logger = logging.getLogger(__name__)

consumer = oauth.Consumer(settings.TWITTER_CLIENT_ID, settings.TWITTER_CLIENT_SECRET)
client = oauth.Client(consumer)

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'

authenticate_url = 'https://api.twitter.com/oauth/authenticate'


class TwitterLogin(APIView):
    def get(self, request, *args, **kwargs):
        # get request token from twitter
        resp, content = client.request(request_token_url, "GET")
        if resp['status'] != '200':
            print(resp, content)
            raise Exception("Invalid response from Twitter.")

        # parse request token and store in temporary token
        data = convert(dict(parse_qsl(content, encoding='utf-8')))
        d = {"request_token": data}
        print(d)
        oauth_token = data['oauth_token']
        print(oauth_token)
        token = TwitterTemporaryToken.objects.create(
            user=request.user,
            request_token=json.dumps(d),
            oauth_token=oauth_token
        )
        token.save()

        # Redirect user to frontend
        url = "%s?oauth_token=%s" % (authenticate_url,
                                     oauth_token)
        return JsonResponse(status=200, data={"auth_url": url})


@login_required
def twitter_logout(request):
    # Log a user out using Django's logout function and redirect them
    # back to the homepage.
    logout(request)
    return HttpResponseRedirect('/')


def twitter_authenticated(request):
    if 'denied' in request.GET:
        return HttpResponseRedirect(settings.FRONTEND_URL)

    oauth_token = request.GET['oauth_token']
    verifier = request.GET['oauth_verifier']

    try:
        temp_token = TwitterTemporaryToken.objects.get(oauth_token=oauth_token)
        data = json.loads(temp_token.request_token)
    except TwitterTemporaryToken.DoesNotExist:
        logger.error("Temporary Token Does Not Exist")
        return HttpResponse(status=404)

    # get request token from temp object
    token = oauth.Token(data['request_token']['oauth_token'],
                        data['request_token']['oauth_token_secret'])

    token.set_verifier(verifier)
    client = oauth.Client(consumer, token)

    # Step 2. Request the authorized access token from Twitter.
    resp, content = client.request(access_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")

    access_token = convert(dict(parse_qsl(content)))

    # Step 3. Lookup the user or create them if they don't exist.
    try:
        twitter_account = TwitterAccount.objects.get(uid=access_token['user_id'], user=temp_token.user)
    except TwitterAccount.DoesNotExist:
        twitter_account = TwitterAccount.objects.create(
            user=temp_token.user,
            uid=access_token['user_id'],
            username=access_token['screen_name']
        )
        twitter_account.save()
        temp_token.delete()

    try:
        token_obj = OAuth2AccessToken.objects.get(account=twitter_account)
    except OAuth2AccessToken.DoesNotExist:
        token_obj = OAuth2AccessToken()
        token_obj.account = twitter_account

    token_obj.token = access_token['oauth_token']
    token_obj.token_secret = access_token['oauth_token_secret']
    token_obj.save()

    fetch_user_info.apply_async((temp_token.user_id, twitter_account.uid), )
    # Todo: some business logic about where to redirect them: first-setup stuff
    return HttpResponseRedirect(settings.FRONTEND_URL)


class TwitterAccounts(ListAPIView):
    authentication_classes = (OAuth2Authentication,)

    serializer_class = AuthorizedTwitterAccountSerializer

    def get_queryset(self):
        print(self.request.user)
        qs = TwitterAccount.objects.filter(user=self.request.user)
        return qs


class RefreshTwitterAccountDetails(APIView):
    authentication_classes = (OAuth2Authentication,)

    def get(self, request, uid, *args, **kwargs):
        try:
            fetch_user_info(request.user.id, uid)
        except TwitterAccount.DoesNotExist:
            return JsonResponse(status=404, data={"message": "This Twitter Account Does Not Exist"})
        except OAuth2AccessToken.DoesNotExist:
            return JsonResponse(status=403, data={"message": "Twitter Authentication Failed"})
        except twitter.error.TwitterError as err:
            return JsonResponse(status=500, data={"message": f"Twitter Verification failed: {err.message}"})
        else:
            acct = TwitterAccount.objects.get(uid=uid, user=request.user)
            serializer = ProfileDetailSerializer(acct, many=False).data
            return JsonResponse(status=200, data=serializer)


class ToggleConfigurationActivity(APIView):
    authentication_classes = (OAuth2Authentication,)

    def post(self, request, uid, *args, **kwargs):
        try:
            twitter_account = TwitterAccount.objects.get(user=request.user, uid=uid)
        except TwitterAccount.DoesNotExist:
            return JsonResponse(status=404, data={"message": "This Twitter Account Does Not Exist"})

        conf = twitter_account.liveconfiguration
        conf.active = not conf.active
        conf.save()
        serializer = ProfileDetailSerializer(twitter_account, many=False).data
        return JsonResponse(data=serializer)


class TwitterConfiguration(APIView):
    """
    View For modifying TwitterAccountDetail
    """
    authentication_classes = (OAuth2Authentication,)

    def get(self, request, uid, *args, **kwargs):
        try:
            qs = TwitterAccount.objects.get(user=request.user, uid=uid)
        except TwitterAccount.DoesNotExist:
            return JsonResponse(status=404, data={"message": "This Twitter Account Does Not Exist"})
        serializer = ProfileDetailSerializer(qs, many=False).data
        return JsonResponse(data=serializer)

    def put(self, request, uid, *args, **kwargs):
        try:
            acct = TwitterAccount.objects.get(user=request.user, uid=uid)
        except TwitterAccount.DoesNotExist:
            return JsonResponse(status=401, data={"message": "You Do Not Have Access or Account Doesnt Exist"})
        config = request.GET.get("config")
        print(request.data)
        if config == "username_config":
            conf = acct.liveconfiguration.usernameconfiguration
            serializer = UsernameConfigurationSerializer(conf, partial=True, data=request.data, many=False)

        else:  # config == "bio_config":
            conf = acct.liveconfiguration.bioconfiguration
            serializer = BioConfigurationSerializer(conf, partial=True, data=request.data, many=False)

        if serializer.is_valid():
            serializer.save()
        else:
            logger.error(serializer.errors)
            return JsonResponse(status=400, data=json.dump(serializer.errors))

        return JsonResponse(data=serializer.data)

    def delete(self, request, uid, *args, **kwargs):
        try:
            acct = TwitterAccount.objects.get(user=request.user, uid=uid)
        except TwitterAccount.DoesNotExist:
            return JsonResponse(status=403, data={"message": "You Do Not Have Access or Account Doesnt Exist"})

        acct.delete()
        return JsonResponse(status=202, data={"message": "Account Deleted"})
