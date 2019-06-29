import os
import json
import tweepy
from elasticsearch import Elasticsearch
from copy import deepcopy


CONSUMER_KEY    = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN    = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET   = os.environ["ACCESS_SECRET"]

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth)
es = Elasticsearch()

def to_iso(time):
    return tweepy.utils.parse_datetime(time).isoformat()

def tweet_parser(data):
    d = deepcopy(data)

    user = deepcopy(d["user"])
    user["created_at"] = to_iso(user["created_at"])

    d.pop("user", None)
    d.pop("entities", None)
    d.pop("extended_entities", None)
    d.pop("quoted_status", None)
    d.pop("retweeted_status", None)
    if "extended_tweet" in d:
        d["text"] = d["extended_tweet"]["full_text"]
        d.pop("extended_tweet")
    d["created_at"] = to_iso(d["created_at"])
    tweet = d

    return (tweet, user)


class ESListener(tweepy.StreamListener):
    def on_status(self, status):
        tweet, user = tweet_parser(status._json)

        es.index(index="users",
                 doc_type="_doc",
                 body=user,
                 id=user["id_str"])

        es.index(index="tweets",
                 doc_type="_doc",
                 body=tweet,
                 id=tweet["id_str"])


listen = ESListener()
stream = tweepy.Stream(auth=api.auth, listener=listen)

stream.sample()
