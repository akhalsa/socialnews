import tweepy
from tweepy import Stream
import json

auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)

class HandleListener(tweepy.StreamListener):
    def on_data(self, data):
        decoded = json.loads(data)
        print "got tweet"
        print decoded
        return True

    def on_error(self, status):
        print status
listen = HandleListener()

stream = tweepy.Stream(auth, listen)
stream.filter(track=['baseball'], async=True)


print " ****************   LOOK AT ME  **************"
time.sleep(5)
stream.disconnect()




