import twitter
import os


def get_api(token):
    api = twitter.Api(consumer_key=os.environ.get("TWITTER_CLIENT_ID"),
                      consumer_secret=os.environ.get("TWITTER_CLIENT_SECRET"),
                      access_token_key=token.token,
                      access_token_secret=token.token_secret)
    return api


def convert(data):
    if isinstance(data, bytes):  return data.decode()
    if isinstance(data, dict):   return dict(map(convert, data.items()))
    if isinstance(data, tuple):  return tuple(map(convert, data))
    if isinstance(data, list):   return list(map(convert, data))
    return data
