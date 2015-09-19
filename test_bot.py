#test twitter posting

import tweepy


auth = tweepy.BasicAuthHandler("FiltraSports", "filtra123")
api = tweepy.API(auth)
api.update_status('hello from tweepy!')