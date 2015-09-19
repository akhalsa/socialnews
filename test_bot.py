#test twitter posting

import tweepy

key = "1mxHCmJv9pQqFsFO9emtgjrSB"
secret = "CcrfJ3WTLqaAigBj0yOhnpAa8bzB6FRG9iIOCVgNktnTgkuHNb"

access_token = "3618709285-bccgXE7SINoljfJbslsWvP8gP5j9AyQV2FELgIx"
token_secret = "GledD6R46Ghy4dIgtEQBhvW4KfI0n2dN6IUGbWFU2qac2"


auth = tweepy.OAuthHandler(key, secret)
auth.set_access_token(access_token, token_secret)
api = tweepy.API(auth)
api.update_status(status = 'hello from tweepy library!')