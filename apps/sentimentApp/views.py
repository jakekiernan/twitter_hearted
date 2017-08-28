# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from django.contrib.sessions.models import Session

import config

class TwitterClient(object):
  
  #Authenticate Twitter user
  def __init__(self):
    con_key = config.keys['consumer_key']
    con_secret = config.keys['consumer_secret']
    acc_token = config.keys['access_token']
    acc_secret = config.keys['access_token_secret']
    try: 
      self.auth = OAuthHandler(con_key, con_secret)
      self.auth.set_access_token(acc_token, acc_secret)
      self.api = tweepy.API(self.auth)
    except:
      print("Error Authenticating")

  #removes links and special characters
  def clean_tweet(self,tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

  def get_tweet_sentiment(self,tweet):
    analysis = TextBlob(self.clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
      return 'positive'
    else:
      return 'negative'

  def get_tweets(self,query,count):
    tweets = []
    try:
      #call Twitter API
      fetched_tweets = self.api.search(q = query, count = count)
      for tweet in fetched_tweets:
        parsed_tweet = {}
        parsed_tweet['text'] = tweet.text
        parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
        if tweet.retweet_count > 0:
          if parsed_tweet not in tweets:
            tweets.append(parsed_tweet)
        else: 
          tweets.append(parsed_tweet)
      return tweets
    except tweepy.TweepError as e:
      print ("Error: " + str(e))

# Create your views here.
def index(request):
  api = TwitterClient()
  try:
    term = request.session['term']
    quantity = request.session['quantity']
    tweets = api.get_tweets(query = term, count = quantity)
    # print tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # print ntweets
    neg = ("Negative tweet percentage: {}%".format(100*len(ntweets)/len(tweets)))
    pos = ("Positive tweet percentage: {}%".format(100*len(ptweets)/len(tweets)))
    hashterm = ("#{term}".format(**locals()))
    return render(request, 'sentimentApp/index.html', {'neg': neg, 'pos': pos, 'term': hashterm})
  except:
    return render(request, 'sentimentApp/index.html')

def tweet(request):
  if request.method == "POST":
    request.session['term'] = request.POST['term']
    request.session['quantity'] = request.POST['quantity']
    return redirect("/")
  else:
		return redirect("/")

def reset(request):
  Session.objects.all().delete()
  return redirect('/')