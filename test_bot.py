#test twitter posting

import tweepy

key = "48jw2ouXpj6AjwLb6BraCZ9cV"
secret = "vtRB7iNur213gIW5qol6A79vZFUAuhDcL34SmnYFuBRkATweco"

access_token = "75fs4ijhWnt2Ss9AkJKsZLQUSd0lRWyfDsVGYKgxc"
token_secret = "P6KajgWHX0eNkEYnI4bGevrroWW9uHuzohl5Gl5uLv6UT"


auth = tweepy.OAuthHandler(key, secret)
auth.set_access_token(access_token, token_secret)
api = tweepy.API(auth)
api.update_status('hello from tweepy library!')