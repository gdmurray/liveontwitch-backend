from liveontwitch.celery import app
from Twitter.models import TwitterAccount
from .serializers import ProfileContentSerializer
from Twitter.models import OAuth2AccessToken as TwitterAccessToken
from Twitter import utils

import logging

logger = logging.getLogger(__name__)


@app.task
def fetch_user_info(user_id, twitter_id):
    logger.info(f"Fetching User Twitter Info: {twitter_id}")
    try:
        twitter_account = TwitterAccount.objects.get(uid=twitter_id, user_id=user_id)

        token = TwitterAccessToken.objects.get(account=twitter_account)
        api = utils.get_api(token)

        user_data = api.GetUser(user_id=twitter_id, return_json=True)
        serializer = ProfileContentSerializer(twitter_account, data=user_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            logger.error(f"Seralizer broke?: {serializer.errors}")
        return
    except TwitterAccount.DoesNotExist:
        logger.error(f"Twitter_Account_Not_Found: {twitter_id}")
    except TwitterAccessToken.DoesNotExist:
        logger.error(f"Twitter_Token_Not_Found: {twitter_id}")

    return


@app.task
def update_username(user_id, twitter_id, configuration):
    try:
        twitter_account = TwitterAccount.objects.get(uid=twitter_id)

        token = TwitterAccessToken.objects.get(account=twitter_account)

        api = utils.get_api(token)
    except TwitterAccount.DoesNotExist:
        print(" do stuff ")
    except TwitterAccessToken.DoesNotExist:
        print(" alert user of no token existing")
