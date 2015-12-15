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


from tornado.options import define, options, parse_command_line
from threading import Thread
from Queue import Queue
from src.DBWrapper import *

import src.CategoryModel

define("port", default=8888, help="run on the given port", type=int)

define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live

auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)


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
        handle_list = getAllHandlesForCategory(local_db, cat_id, self.request.remote_ip)
        votes_this_hour = getVoteCountByIpForTimeFrame(local_db, self.request.remote_ip, 3600)
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
        
        votes_this_hour = getVoteCountByIpForTimeFrame(local_db, self.request.remote_ip, 3600)
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
                user_id = re.escape(str(user.id))
                username = re.escape(user.name)
                profile_link = user.profile_image_url
                if(user_id != None):
                    createHandle(local_db,user_id, username, re.escape(twitter_handle), profile_link )
                    table_info = findTableInfoWithTwitterHandle( re.escape(twitter_handle), local_db)
            except Exception, e:
                print "failed to insert :/"
                print e
                self.finish("bad handle/insertion")
                return
        insertVote(local_db, self.request.remote_ip, cat_id, table_info["twitter_id"], table_info["twitter_name"], table_info["twitter_handle"] , upvote )
        
        self.finish("200")
        
        
    
    

    
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
                
                lookup = getTweetOccurances(time_frame_seconds, str(cat_id), local_db)
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
            self.finish(json.dumps([]))
            return
        
        response = api.search_users(search_string, 5, 1);

        self.finish(response)
    
class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("static/index.html")
        
app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
    (r"/category/(.*)", HandleListForCategoryId),
    (r"/handle/(.*)/category/(.*)/upvote/(.*)", HandleVoteReceiver),
    (r"/category", Category),
    (r'/reader/(.*)/time/(.*)', Reader),
    (r'/page_load/twitter_id/(.*)',  PageLoad),
    (r'/twitter/search/(.*)', Twitter)
])

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