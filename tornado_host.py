import tornado.ioloop
import tornado.web
import tornado.websocket
import os, uuid
import socket   #for sockets
import sys  #for exit
import json
import MySQLdb
import tweepy
import thread
import urllib2
import threading
import datetime
import requests
import argparse
import re
import hashlib


from tornado.options import define, options, parse_command_line
from threading import Thread
from Queue import Queue
from src.DBWrapper import *
from passlib.hash import sha256_crypt


define("port", default=8888, help="run on the given port", type=int)

define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live

auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)

class AuthBase(tornado.web.RequestHandler):
    def getUserId(self, db):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        
        email = self.get_secure_cookie("email")
        password_hash = self.get_secure_cookie("password_hash")
        if not email:
            print "no email"
        if not password_hash:
            print "no password"
        
        if(email):
            print email
        if(password_hash):
            print password_hash
            
        user_id = getUserIdWithIpAddressCreds(db, remote_ip, email, password_hash)
        return user_id


class Category(tornado.web.RequestHandler):    
    def get(self, ):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        self.finish(json.dumps(getCategoryStructure(local_db)))

class HandleListForCategoryId(tornado.web.RequestHandler):
    def get(self, cat_name):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        #this should get the full list of handles and their scores in the category
        cat_id = findCategoryIdWithName(re.escape(cat_name), local_db)
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        
        email = self.get_secure_cookie("email")
        password_hash = self.get_secure_cookie("password_hash")
        if not email:
            print "no email"
        if not password_hash:
            print "no password"
        
        if(email):
            print email
        if(password_hash):
            print password_hash
            
        user_id = getUserIdWithIpAddressCreds(local_db, remote_ip, email, password_hash)
        
        
        handle_list = getAllHandlesForCategory(local_db, cat_id, user_id)
        votes_this_hour = getVoteCountByIpForTimeFrame(local_db, user_id, 3600)
        print "got handle list:"
        self.finish(json.dumps({"handles":handle_list, "remaining_votes":(10 - votes_this_hour)}))
        
                    

class HandleVoteReceiver(tornado.web.RequestHandler):
    def post(self,twitter_handle, category_name, positive  ):
        #first check to see if this ip address has been used more than 5 times
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        
        email = self.get_secure_cookie("email")
        password_hash = self.get_secure_cookie("password_hash")
        if not email:
            print "no email"
        if not password_hash:
            print "no password"
        
        if(email):
            print email
        if(password_hash):
            print password_hash
            
        user_id = getUserIdWithIpAddressCreds(local_db, remote_ip, email, password_hash)
        
        
        votes_this_hour = getVoteCountByIpForTimeFrame(local_db, user_id, 3600)
        print "found votes this hour of: "+str(votes_this_hour)
        if(votes_this_hour >= 10):
            self.finish("{'message':'you are out of votes, please wait for them to recharge}")
            return
        
        upvote = False
        if(positive == "1"):
            upvote = True
        elif (positive == "-1"):
            upvote = False
        else:
            self.finish("bad vote value")
            return
        ##########REMEMBER you have a boolean translation layer between restful value "positive" that gets switched to a boolean
        ######for now this is fine because it also adds some security
        ###########but dont forget!!!!!!
        
        cat_id = findCategoryIdWithName(re.escape(category_name), local_db)
        if(cat_id == 0):
            self.finish("bad category name")
            return
        
        
        table_info = findTableInfoWithTwitterHandle( re.escape(twitter_handle), local_db)
        print "table info for that handle is: "+str(table_info)
        
        if(table_info == None):
            try:
                user = api.get_user(screen_name = twitter_handle)
                twitter_handle = "@"+user.screen_name
                twitter_user_id = re.escape(str(user.id))
                username = re.escape(user.name)
                profile_link = user.profile_image_url
                if(twitter_user_id != None):
                    createHandle(local_db,twitter_user_id, username, twitter_handle, profile_link )
                    table_info = findTableInfoWithTwitterHandle( twitter_handle, local_db)
                else:
                    print "couldnt find: "+twitter_handle
            except Exception, e:
                print "failed to insert :/"
                print e
                self.finish("bad handle/insertion")
                return
        
        
        if(alreadyVoted(local_db, user_id,  cat_id, table_info["twitter_id"])):
            print "already voted returned true"
            self.finish("{'message': 'you already voted for this handle'}")
            return
        
        insertVote(local_db, user_id, cat_id, table_info["twitter_id"], table_info["twitter_name"], table_info["twitter_handle"] , upvote )
        
        self.finish("200")
        
        
    
    
class SizedReader(tornado.web.RequestHandler):
    def get(self, cat, size, time_frame_seconds):
        local_db = MySQLdb.connect(
            host=host_target,
            user="akhalsa",
            passwd="sophiesChoice1",
            db="newsdb",
            charset='utf8',
            port=3306)
        print "cat: "+cat
        print "seconds: "+time_frame_seconds
        print "size: "+size
        cat_id = findCategoryIdWithName(cat, local_db)
        if(cat_id == 0):
            self.finish("Category Error, Try Again")
        print "found category id: "+str(cat_id)        
        
        lookup = getTweetOccurances(time_frame_seconds, str(cat_id), local_db, size)
        self.finish(json.dumps(lookup))

    
class Reader(tornado.web.RequestHandler):
        def get(self, cat, time_frame_seconds):
                local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
                print "cat: "+cat
                print "seconds: "+time_frame_seconds
                cat_id = findCategoryIdWithName(cat, local_db)
                if(cat_id == 0):
                        self.finish("Category Error, Try Again")
                print "found category id: "+str(cat_id)        
                
                lookup = getTweetOccurances(time_frame_seconds, str(cat_id), local_db, 30)
                self.finish(json.dumps(lookup))
                
class PageLoad(tornado.web.RequestHandler):
    def get(self, twitter_id):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        twitter_id = re.escape(twitter_id)
        tweet_dict = getTweetWithTwitterId(local_db, twitter_id)
        if(tweet_dict["checked"] == 0):
            updateTweet(tweet_dict["text"], twitter_id, local_db)
        tweet_dict = getTweetWithTwitterId(local_db, twitter_id)
        self.finish(json.dumps(tweet_dict))
        
class Twitter(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, search_string):
        if(search_string == ""):
            self.finish(json.dumps({"search":"", "handles":""}))
            return
        
        response = api.search_users(search_string, 5, 1);
        response_list = []
        for user in response:
            response_list.append({"name":user.name, "twitter_id": user.id, "screen_name":user.screen_name})
        
        response_full = {"search":search_string, "handles":response_list}
        
        print json.dumps(response_full)
        self.finish(json.dumps(response_full))
        
class TwitterTimeline(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, search_string):
        response = api.user_timeline(screen_name=search_string, count=5)
        tweets = []
        for status in response:
            target_url = "https://api.twitter.com/1/statuses/oembed.json?id="+str(status.id)
            print target_url
            response = urllib2.urlopen(target_url)
            dictionary = json.loads(response.read())
            tweets.append(dictionary["html"])
            
        self.finish(json.dumps(tweets))
    
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html")
        
class IndexCategoryHandler(tornado.web.RequestHandler):
    def get(self, cat):
        print "injecting cat: "+cat
        self.render("static/cat_index.html", cat_name=cat)
        
        
class NewIndexHandler(tornado.web.RequestHandler):
    def get(self):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        self.render("static/index.html")
        
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/login.html")
        
class TweetHandler(tornado.web.RequestHandler):
    def get(self, tweet_id):
        self.render("static/tweet.html",  t_id=tweet_id)
    
class TweetAPI(AuthBase):
    def get(self, tweet_id):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        getTweetWithId(local_db, tweet_id)
        
    def post(self, tweet_id):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        #get comment structure from post body
        data = json.loads(self.request.body)
        #get user id
        user_id = self.getUserId(local_db)
        insertComment(local_db, tweet_id, user_id, re.escape(data["comment_text"]))
        
        
        

        
class LoginAPI(tornado.web.RequestHandler):
    def get(self):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        email = self.get_secure_cookie("email")
        password_hash = self.get_secure_cookie("password_hash")
        if not email or not password_hash:
            print "no password"
            self.finish(json.dumps({"username":None }))
            return
        print "checking email: "+email+" with pw hash: "+password_hash
        
        user = getUserWithCredentials(local_db, email, password_hash)
        username = re.sub(r'\\(.)', r'\1', user["username"])
        output = json.dumps({"username": username})
        print "sending: "+output
        self.finish(output)
        return
    
    def put(self):
        #this is a logout mechanism
        #find username and password 
        data = json.loads(self.request.body)
        if(not "logout" in data):
            print "log out failure"
            self.finish({"success":False})
            return
        
        self.clear_cookie("email")
        self.clear_cookie("password_hash")
        
        self.finish({"success":True})
        
        
    def post(self):
        #this is a login mechanism
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        data = json.loads(self.request.body)
        pw_hash = hashlib.sha224(data["password"]).hexdigest()
        print "generated hash: "+pw_hash
        email = re.escape(data["email"])
        user = getUserWithCredentials(local_db, email, pw_hash)
        if(user is None):
            print "user was none :/"
            self.finish(json.dumps({"result": "Invalid Credentials"}))
            return
        else:
            print "logged in man"
            self.set_secure_cookie("email", email)
            self.set_secure_cookie("password_hash",pw_hash)
            username = re.sub(r'\\(.)', r'\1', user["username"])
            self.finish(json.dumps({"username": username}))
            return
        
        
        
    
class signupAPI(tornado.web.RequestHandler):
    

    def post(self):
        #find username and password 
        data = json.loads(self.request.body)
        pw_hash = hashlib.sha224(data["password"]).hexdigest()
        print "generated hash: "+pw_hash
        email = re.escape(data["email"])
        username = re.escape(data["username"])
        
        #need to check if this is a valid user already
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        user = getUserWithCredentials(local_db, email, pw_hash)
        if(user is None):
            if(checkForExistingEmail(local_db, email)):
                print "found existing user with different creds"
                print "pw_hash: "+pw_hash
                self.finish(json.dumps({"error": "Invalid token"}))
                return
            
            #ok no existing user
            #lets create one
            insertUserWithValues(local_db, email, pw_hash, username)

        
        self.set_secure_cookie("email", email)
        self.set_secure_cookie("password_hash",pw_hash)
        username = re.sub(r'\\(.)', r'\1', username)
        print "outputting username: "+username
        self.finish(json.dumps({"username": username}))
        
    

        
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "ePbbBygvlUDmoiOCBVuy"
}
app = tornado.web.Application([
    (r'/c/(.*)', IndexCategoryHandler),
    (r'/', NewIndexHandler),
    (r'/login', LoginHandler),
    (r'/tweet/(.*)', TweetHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
    (r"/category/(.*)", HandleListForCategoryId),
    (r"/handle/(.*)/category/(.*)/upvote/(.*)", HandleVoteReceiver),
    (r"/category", Category),
    (r'/reader/(.*)/time/(.*)', Reader),
    (r'/page_load/twitter_id/(.*)',  PageLoad),
    (r'/twitter/search/(.*)', Twitter),
    (r'/twitter/timeline/(.*)', TwitterTimeline),
    (r"/api/reader/(.*)/size/(.*)/time/(.*)", SizedReader),
    (r"/api/signup", signupAPI),
    (r"/api/login", LoginAPI),
    (r"/api/tweet/(.*)", TweetAPI)
], **settings)

if __name__ == '__main__':
    
    
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
    elif(options.mysql_host == 1):
        host_target = host_dev
        
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    ####################
    #FIX SQL going away bug
    #http://stackoverflow.com/questions/207981/how-to-enable-mysql-client-auto-re-connect-with-mysqldb
    #####################