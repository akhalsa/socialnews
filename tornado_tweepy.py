import tornado.ioloop
import tornado.web
import tornado.websocket
import os, uuid
import socket   #for sockets
import sys  #for exit
import json
import MySQLdb
import tweepy
from tornado.options import define, options, parse_command_line
from threading import Thread

define("port", default=8888, help="run on the given port", type=int)

db = MySQLdb.connect(
        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        port=3306)


auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)

class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        #decoded = json.loads(data)

        # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
        #print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
        #print ''
        print "transmitting data"
        #fetch original tweet
        decoded = json.loads(data)
        if("retweeted_status" in decoded):
                output_data = decoded['retweeted_status']
                
        else:
                
                output_data = decoded
                
        print "sending with screen name: "+output_data['user']['screen_name']
        try:
                self.wsHandle.write_message(json.dumps(output_data))
        except tornado.websocket.WebSocketClosedError:
            print "web socket closed"
            return False
        
        return True

    def on_error(self, status):
        print status
        
        
class HandleListener(tweepy.StreamListener):
        def __init__(self):
                self.setupSocket()

                
        def setupSocket(self, ):
                auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
                auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
                stream = tweepy.Stream(auth, self)
                stream.filter(follow=getAllTwitterIds())
                
        def on_data(self, data):
                decoded = json.loads(data)
                #print "recevied: "+str(decoded)
                #check if user for tweet
                
                if(findTableIdWithTwitterId(str(decoded['id'])) != 0):
                        print "recevied tweet from: "+str(decoded['id'])+" with text: "+decoded['text']
                elif("retweeted_status" in decoded):
                        print "original id is: "+str(decoded['id'])
                        decoded = decoded['retweeted_status']
                        print "we now have a source id of: "+str(decoded['id'])
                        source_id = findTableIdWithTwitterId(str(decoded['id']))
                        if(source_id != 0):
                                print "recevied retweet for: "+getHandleForLocalId(str(source_id))+" with text: "+decoded['text']
                        else:
                                print "this was a retweet, but wasnt a trusted source?!?!"
                else:
                        print "this wasn't a retweet AND wasn't from a trusted source!?!"

                return True

        def on_error(self, status):
                print status

def getAllTwitterIds():
        cursor = db.cursor()
        sql = "SELECT twitter_id FROM TwitterSource;"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        return return_list

def getCategoriesWithSourceId(source_id):
        cursor = db.cursor()
        sql = "SELECT category_id FROM SourceCategoryRelationship WHERE source_id like "+str(source_id)+";"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        return return_list
        
def getTwitterIdForLocalId(local_id):
        cursor = db.cursor()
        sql = "SELECT twitter_id FROM TwitterSource WHERE ID like "+str(local_id)+";"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
                return_id = row[0]
        cursor.close()    
        return return_id

def findTableIdWithTwitterId(twitter_id):
        cursor = db.cursor()
        sql = "SELECT ID FROM TwitterSource WHERE twitter_id like '"+twitter_id+"';"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
            return_id = row[0]
        cursor.close()    
        return return_id

def getHandleForLocalId(local_id):
        cursor = db.cursor()
        sql = "SELECT handle FROM TwitterSource WHERE ID like '"+local_id+"';"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
            return_id = row[0]
        cursor.close()    
        return return_id

def findCategoryIdWithName(cat_name):
    cursor = db.cursor()
    sql = "SELECT ID FROM Category WHERE Name like '"+cat_name+"';"
    cursor.execute(sql)
    return_id = 0
    for row in cursor.fetchall() :
        return_id = row[0]
    cursor.close()    
    return return_id



def getListOfHandlesForCategoryId(cat_id):
    cursor = db.cursor()
    return_list = []
    sql = "SELECT twitter_id From TwitterSource WHERE ID in (SELECT source_id From SourceCategoryRelationship WHERE category_id="+str(cat_id)+");"
    cursor.execute(sql)
    for row in cursor.fetchall() :
        return_list.append(str(row[0]))
    cursor.close()
    return return_list

def setup_socket_handler(arg, web_socket):
    print "got a new message"
    print arg
    print "this is a category id of: "+str(findCategoryIdWithName(arg))
    #one filter per category?
    #one filter per handle with category entries -> lower bandwidth
    
    category_id = findCategoryIdWithName(arg)
    print "this yields handles of: "
    print getListOfHandlesForCategoryId(category_id)
    l = StdOutListener()
    l.wsHandle = web_socket
    auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
    auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
    stream = tweepy.Stream(auth, l)
    stream.filter(follow=getListOfHandlesForCategoryId(category_id))



class Source(tornado.web.RequestHandler):

    def post(self):
        
        user_id = False
        username = ""
        for key in self.request.arguments:
            #find the handle
            if(key == "Handle"):
                user = api.get_user(screen_name = self.request.arguments[key][0])
                user_id = str(user.id)
                username = user.name
                print "user_id: "+user_id+" and name: "+username
               
        if(user_id is not False):
            cursor = db.cursor()
            #create user entry
            sql = "INSERT INTO TwitterSource(Name, handle, twitter_id) VALUES ('"+username+"','"+self.request.arguments[key][0]+"', '"+user_id+"')"
            try:
                # Execute the SQL command
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()
            except:
                # Rollback in case there is any error
                print "error on insertion"
                db.rollback()
            cursor.close()
            
            #create relationships to categories
            for key in self.request.arguments:
                if("cat" in key):
                    
                    cat_id = findCategoryIdWithName(self.request.arguments[key][0])
                    user_db_id = findTableIdWithTwitterId(user_id)
                    sql = "INSERT INTO SourceCategoryRelationship(source_id, category_id) VALUES ("+str(user_db_id)+", "+str(cat_id)+");"
                    cursor = db.cursor()
                    try:
                        # Execute the SQL command
                        cursor.execute(sql)
                        # Commit your changes in the database
                        db.commit()
                    except:
                        # Rollback in case there is any error
                        print "error on insertion"
                        db.rollback()
                    cursor.close()
                    
                else:
                    print "dropping key: "+key
            
            
        else :
            print "no user id found"
        self.finish()
        
class Category(tornado.web.RequestHandler):
    def post(self):
        title = self.get_argument('Title', '')
        parent_cat = self.get_argument('parent', '')
        cursor = db.cursor()
        #first locate the ID if there is one of the parent Category
        sql = """SELECT ID From Category WHERE Name Like '"""+parent_cat+"""';""";
        cursor.execute(sql)
        
        new_id = "NULL"
        for row in cursor.fetchall() :
            new_id = row[0]
        
        
        
        sql = "INSERT INTO Category(Name, Parent) VALUES ('"+title+"', "+str(new_id)+")"
        print "inserting with: "+sql
        
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except:
            # Rollback in case there is any error
            print "error on insertion"
            db.rollback()
            
        cursor.close()
        self.finish()
        
    def get(self, id):
        print "running get with id: "+str(id)
        self.finish()
        
    def get(self, ):
        cur = db.cursor()
        cur.execute("SELECT * FROM Category")
        
        output_array = []
        for row in cur.fetchall():
            print ("appending: "+row[1])
            output_map = dict()
            output_map["Name"] = row[1]
            output_array.append(output_map)
        cur.close()
        self.finish(json.dumps(output_array))
    
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    #self.write_message(data, True)
    
    def open(self, *args):
        print 'new connection'

    def on_message(self, message):
        thread = Thread(target = setup_socket_handler, args = (message, self))
        thread.start()
        print "on_meesage closed"
        

    def on_close(self):
        print "closing"



app = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
    (r"/category", Category),
    (r"/source", Source),
    (r'/ws', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    handle = HandleListener()
    ##############################
    # Note: this approach does not work. you need to set up a single stream for ALL handles we care about
    # Then for each incoming tweet, we want to look at the text, and determine categories by looking for a known handle in the id OR retweeted id
    # This can be done using a hash lookup for big O of 1 instead of N as this operation will be done very frequently
    # This approach will require a system reboot each time new handles get added
    # this is probably not the end of the world for now
    ##############################
    
    print "done loading handles"
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()