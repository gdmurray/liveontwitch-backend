import logging

from django import apps

from liveontwitch.celery import app
from Twitter import utils
# from twitch.models import TwitchEvent
from .serializers import ProfileContentSerializer
from .models import LiveConfiguration, BioConfiguration, UsernameConfiguration, \
    TwitterAccount, OAuth2AccessToken as TwitterAccessToken
import twitter

logger = logging.getLogger(__name__)


@app.task
def fetch_user_info(user_id, twitter_id, api=None):
    logger.info(f"Fetching User Twitter Info: {twitter_id}")
    try:
        twitter_account = TwitterAccount.objects.get(user_id=user_id, uid=twitter_id)

        if not api:
            token = TwitterAccessToken.objects.get(account=twitter_account)
            api = utils.get_api(token)

        user_data = api.GetUser(user_id=twitter_id, return_json=True)
        serializer = ProfileContentSerializer(twitter_account, data=user_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            logger.error(f"Seralizer broke?: {serializer.errors}")
        return serializer.data

    except TwitterAccount.DoesNotExist:
        logger.error(f"Twitter_Account_Not_Found: {twitter_id}")
        raise TwitterAccount.DoesNotExist
    except TwitterAccessToken.DoesNotExist:
        logger.error(f"Twitter_Token_Not_Found: {twitter_id}")
        raise TwitterAccessToken.DoesNotExist


@app.task
def handle_twitch_event(event_id):
    # Circular Import Avoidance
    logger.info(f"Handling Twitch Event Id: {event_id}")
    event_model = apps.apps.get_model('twitch', 'twitchevent')

    event = event_model.objects.get(pk=event_id)
    twitch_account = event.account

    twitter_accounts = TwitterAccount.objects.filter(user=twitch_account.user)

    for twitter_account in twitter_accounts:
        try:
            token = TwitterAccessToken.objects.get(account=twitter_account)
            api = utils.get_api(token)
            configuration = LiveConfiguration.objects.get(account=twitter_account)
            if configuration.active:
                u_conf = configuration.usernameconfiguration
                b_conf = configuration.bioconfiguration
                most_recent_info = fetch_user_info(twitter_account.user_id, twitter_account.uid, api)

                if event.action == event_model.ONLINE:
                    logger.debug("ONLINE EVENT")
                    # Username Configuration
                    if u_conf.active:
                        if u_conf.live_text not in [None, '']:
                            if u_conf.positioning == UsernameConfiguration.BEFORE:
                                updated_username = u_conf.live_text + ' ' + most_recent_info['name']
                            else:
                                updated_username = most_recent_info['name'] + ' ' + u_conf.live_text

                            api.UpdateProfile(name=updated_username)
                            logger.error(f"MODIFIED_USERNAME: {updated_username}")
                            twitter_account.modified_name = updated_username
                            twitter_account.modified_hold = True
                            twitter_account.save()

                    # Bio Configuration
                    if b_conf.active:
                        if b_conf.live_text not in [None, '']:
                            if b_conf.positioning == BioConfiguration.BEFORE:
                                updated_bio = b_conf.live_text + ' ' + most_recent_info['description']
                            else:
                                updated_bio = most_recent_info['description'] + ' ' + b_conf.live_text

                            api.UpdateProfile(description=updated_bio)

                            twitter_account.modified_bio = updated_bio
                            twitter_account.modified_hold = True
                            twitter_account.save()
                elif event.action == event_model.OFFLINE:
                    logger.debug("OFFLINE EVENT")
                    if twitter_account.modified_hold:
                        if u_conf.active:
                            api.UpdateProfile(name=twitter_account.username)
                        if b_conf.active:
                            api.UpdateProfile(description=twitter_account.description)

                        twitter_account.modified_hold = False
                        twitter_account.modified_name = None
                        twitter_account.modified_bio = None
                        twitter_account.save()
        except twitter.error.TwitterError as err:
            logger.error(f"Error Authenticating API for: {twitter_account.uid} - {err.message}")
            continue
        except TwitterAccessToken.DoesNotExist:
            logger.error(f"No Twitter Access Token for: {twitter_account.uid}")
            continue
        except LiveConfiguration.DoesNotExist:
            logger.error(f"No Configuration for {twitter_account.uid}")
            continue
