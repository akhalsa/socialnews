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
import simplejson


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
    
    def getUserName(self, db):
        user_id = self.getUserId(db)
        return getUserNameForId(db, user_id)
        
    def isLoggedIn(self, db):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        
        email = self.get_secure_cookie("email")
        password_hash = self.get_secure_cookie("password_hash")
        if not email:
            print "no email"
        if not password_hash:
            print "no password"

        
        if(email and password_hash):
            return isValidCreds(db, email, password_hash)
        else:
            return False
    


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

class HandleListForCategoryId(AuthBase):
    def get(self, cat_name):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        user_id = self.getUserId(local_db)
        
        cat_id = findCategoryIdWithName(re.escape(cat_name), local_db)

        
        handle_list = getAllHandlesForCategory(local_db, cat_id, user_id)
        print "got handle list: "+str(handle_list)
        self.finish(json.dumps({"handles":handle_list}))
        
                    

class HandleVoteReceiver(AuthBase):
    def post(self,twitter_handle, category_name, positive  ):
        #401 = rate limit exceeded
        ##405 = the user already voted for this tweet
        
        
        #first check to see if this ip address has been used more than 5 times
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        data = json.loads(self.request.body)
        print "tweet_id"+data["tweet_id"]
        tweet_id = re.escape(data["tweet_id"])
        
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
        logged_in = self.isLoggedIn( local_db)
        
        if (not logged_in) and (votes_this_hour >= 5):
            ## 401 means the user has exceeded rate limits
            self.clear()
            self.set_status(401)
            self.finish()
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

            
        new_handle = not checkForFirstVote(local_db, cat_id, table_info["twitter_id"])


        if(new_handle):
            #select all the categorys above this one for the vote
            chain = categoryChainForCategory(local_db, cat_id)
            print "Inserting Chain: "+str(chain)
            vote_array = []
            for index, val in enumerate(chain):
                vote_array.append(20/(index+1))
                    
            print "will vote with chain: "+str(chain)
            print "will vote with vote_Array: "+str(vote_array)
            
            insertVote(local_db, user_id, chain, table_info["twitter_id"], vote_array)
        else:
            if tweet_id is None:
                self.clear()
                self.set_status(400)
                self.finish()
                return
            
            if(alreadyVoted(local_db, user_id, tweet_id, cat_id, table_info["twitter_id"])):
                ##405 means the user already voted for this tweet
                self.clear()
                self.set_status(405)
                self.finish()
                return
            print "Inserting non Chain"+str([cat_id])
            vote_val = 1 if upvote else -1
            insertTweetVote(local_db, user_id, [cat_id], table_info["twitter_id"] ,tweet_id, [vote_val] )
    
        self.clear()
        self.set_status(200)
        self.finish()
        
        
    
    
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
        self.finish(simplejson.dumps(lookup))

    
class Reader(AuthBase):
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
                if(len(lookup) == 0):
                    self.finish(simplejson.dumps(lookup))
                    return
                
                user_id = self.getUserId(local_db)
                ids = []
                for tweet in lookup:
                    tweet["voted"] = 0
                    tweet["top_comment"] = {"total_comment_count":0}
                    ids.append(tweet["id"])
                    
                user_vote = userVote(local_db, user_id, ids)
                
                for vote_entry in user_vote:
                    for tweet in lookup:
                       if(tweet["id"] == vote_entry):
                            tweet["voted"] = user_vote[vote_entry]
                            
                            
                top_comments = topComments(local_db, ids )
                
                for comment in top_comments:
                    for tweet in lookup:
                        if(tweet["id"] == comment):
                            tweet["top_comment"] = top_comments[comment]
                            
                            
                print simplejson.dumps(lookup)
                self.finish(simplejson.dumps(lookup))
                
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
        self.render("static/new_cat_index.html", cat_name=cat)
        
        
class NewIndexHandler(tornado.web.RequestHandler):
    def get(self):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        self.render("static/new_cat_index.html", cat_name="media")
        
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/login.html")
        
class TweetHandler(tornado.web.RequestHandler):
    def get(self, tweet_id):
        self.render("static/tweet.html",  t_id=tweet_id)

class CommentVoteAPI(AuthBase):
    def post(self, comment_id):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        user_id = self.getUserId(local_db)
        data = json.loads(self.request.body)
        comment_id = re.escape(str(data["comment_id"]))
        value = data["vote_val"]
        if(value == 1):
            value = 1
        else:
            value = -1
            
        #do some rate checking
        
        if(alreadyVotedForComment(local_db, user_id, comment_id)):
            ##405 means the user already voted for this tweet
            self.clear()
            self.set_status(405)
            self.finish()
            return
        logged_in = self.isLoggedIn( local_db)
        if ((not logged_in) and (getCommentVoteCountByIpForTimeFrame(local_db, user_id, 3600) >= 5)):
            ##401 means the rate limit exceeded
            self.clear()
            self.set_status(401)
            self.finish()
            return
        
        insertCommentVote(local_db, user_id, comment_id, value)
        self.clear()
        self.set_status(200)
        self.finish()
    
class TweetAPI(AuthBase):
    def get(self, tweet_id):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        user_id = self.getUserId(local_db)
        print "loading tweet with id: "+str(user_id)
        self.finish(simplejson.dumps(getTweetWithId(local_db, tweet_id, user_id)))
        
        
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
        ###will need to rate check here for anonymous users
        logged_in = self.isLoggedIn( local_db)
        if(not logged_in):
            ##check comment count
            comment_count = userCommentCount(local_db, user_id)
            if(comment_count > 5):
                self.clear()
                self.set_status(401)
                self.finish()
                return
        
        insertComment(local_db, tweet_id, user_id, re.escape(data["comment_text"]))
        self.clear()
        self.set_status(200)
        self.finish()
        
        

        
class LoginAPI(AuthBase):
    def get(self):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        user_id = self.getUserId(local_db)
        username = self.getUserName(local_db)
        if(username == None):
            username = "user"+str(user_id)
            
        logged_in = self.isLoggedIn( local_db)
        self.finish(json.dumps({"user_id": user_id, "username":username, "logged_in": logged_in}))
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
        
        self.clear()
        self.set_status(200)
        self.finish()
        
        
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
            self.clear()
            self.set_status(403)
            self.finish()
            return
        else:
            print "logged in man"
            self.set_secure_cookie("email", email)
            self.set_secure_cookie("password_hash",pw_hash)
            username = re.sub(r'\\(.)', r'\1', user["username"])
            self.finish(json.dumps({"username": username, "logged_in":True }))
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
                #there is no user with THESE credentials
                #but there is a user wiht that email
                #as such throw exception
                self.clear()
                self.set_status(403)
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
    (r'/reader/(.*)/time/(.*)', Reader),
    (r'/page_load/twitter_id/(.*)',  PageLoad),
    (r'/twitter/search/(.*)', Twitter),
    (r'/twitter/timeline/(.*)', TwitterTimeline),
    (r"/api/reader/(.*)/size/(.*)/time/(.*)", SizedReader),
    (r"/api/signup", signupAPI),
    (r"/api/login", LoginAPI),
    (r"/api/tweet/(.*)/vote", CommentVoteAPI),
    (r"/api/tweet/(.*)", TweetAPI),
    (r"/api/category", Category)
    
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