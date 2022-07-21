"""
In this module there are two methods for scrapping tweets.
First it was implemented the scrap_with_tweepy but the `tweet_mode="extended"` is
not working properly, returning the tweets cropped.

As a solution a second method is implemented using twython; at the moment
of this writing, the extended mode functions as supposed to.
"""

from datetime import datetime
from twython import Twython, TwythonError
import tweepy
import sys
import yaml
import pandas as pd


def scrap_with_tweepy(hashtag: str) -> None:
    with open("twitter-twitter-credentials.yaml", "r") as stream:
        configs = yaml.safe_load(stream)

    api_key = configs["api_key"]
    api_key_secret = configs["api_key_secret"]
    access_token = configs["access_token"]
    access_token_secret = configs["access_token_secret"]

    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    tweets = []
    num_tweets_limit = 750
    for tweet in tweepy.Cursor(api.search_tweets, q=hashtag, tweet_mode="extended").items(num_tweets_limit):
        date = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
        text = tweet.full_text.replace('\n', ' ')
        tweets.append((date, text))
    columns = ['date', 'text']
    df = pd.DataFrame(tweets, columns=columns)
    df.to_csv(f"{hashtag}_tweets_{datetime.today().strftime('%Y-%m-%d_%H:%M')}.csv", index=False, sep="|")


def scrap_with_twython() -> None:
    #### PARAMETERS ####
    hashtags = ["#Λιγνάδης", "#Λιγναδης_gate", "#lignadis"]
    keywords = ['Λιγνάδης', 'καλλιτεχνικού διευθυντή', 'καλλιτεχνικός διευθυντής', 'επίδαυρος', 'επιδαύρου']
    ####################

    with open("twitter-credentials.yaml", "r") as stream:
        configs = yaml.safe_load(stream)

    api_key = configs["api_key"]
    api_key_secret = configs["api_key_secret"]
    access_token = configs["access_token"]
    access_token_secret = configs["access_token_secret"]

    twitter = Twython(
        api_key,
        api_key_secret,
        access_token,
        access_token_secret
    )

    tweets_list = []

    # Scrap tweets of newspapers and keep only the ones that contain our hashtags
    newspapers = ('Kathimerini_gr', 'protothema', 'efsyntakton',
                  'Newsbeast', 'ta_nea', 'tovimagr')
    for newspaper in newspapers:
        try:
            tweets = twitter.get_user_timeline(screen_name=newspaper, q='', count=100, tweet_mode='extended')
        except TwythonError as e:
            print("Error getting tweets:", e)

        relevant_tweets = []
        for tweet in tweets:
            date_string = tweet["created_at"]
            date = datetime.strptime(date_string, '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:00')
            text = tweet["full_text"]

            for keyword in keywords:
                if keyword.lower() in text.lower():
                    relevant_tweets.append((date, text))
        if relevant_tweets:
            print(f"Scrapped {len(relevant_tweets)} relevant tweet(s) from {newspaper}.")
            tweets_list.extend(relevant_tweets)

    # Scrap tweets from random users
    for hashtag in hashtags:
        try:
            tweets = twitter.search(q=hashtag, count=100, tweet_mode='extended')
        except TwythonError as e:
            print("Error getting tweets:", e)
        print(f"Scrapped {len(tweets['statuses'])} tweet(s) for hashtag: {hashtag}")
        for tweet in tweets["statuses"]:
            date_string = tweet["created_at"]
            date = datetime.strptime(date_string, '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:00')
            text = tweet["full_text"]
            tweets_list.append((date, text))

    # Export findings to csv
    columns = ['date', 'text']
    pd.DataFrame(tweets_list, columns=columns).to_csv(
        f"{hashtag}_tweets_{datetime.today().strftime('%Y-%m-%d_%H:%M')}.csv",
        index=False, sep="|"
    )


if __name__ == '__main__':
    available_methods = ('tweepy', 'twython')

    method = sys.argv[1]

    if method not in available_methods:
        raise ValueError(f'Incorrect method. Please choose one of the following: {available_methods}')

    if method == 'tweepy':
        hashtag = sys.argv[2]
        scrap_with_tweepy(hashtag)
    elif method == 'twython':  # Best method 💪
        scrap_with_twython()

