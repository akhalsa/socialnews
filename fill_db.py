#populate profile picture url

import MySQLdb
import tweepy

auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)

db = MySQLdb.connect(
        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)
        

def getAllTwitterIds():
        print "attempting to acquire lock at getAll187"
        print "successfully acquired lock at 187"
        cursor = db.cursor()
        sql = "SELECT twitter_id FROM TwitterSource;"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        return return_list

def updateIdWithLinkString(twitter_id, profile_link):
        cursor = db.cursor()
        #create user entry
        sql = "Update TwitterSource SET profile_image = '"+profile_link+"' WHERE ID like "+str(twitter_id)+";"
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

for twitter_id in getAllTwitterIds():
        user = api.get_user(user_id = twitter_id)
        updateIdWithLinkString(twitter_id, user.profile_image_url)
        #print "User: "+ user.screen_name+" with link "+user.profile_image_url
        #user_id = str(user.id)
        #username = user.name
        #print "user_id: "+user_id+" and name: "+username