import MySQLdb
from tornado.options import define, options, parse_command_line

define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live


if __name__ == '__main__':
   parse_command_line()
   if(options.mysql_host == 0):
       host_target = host_live
   elif(options.mysql_host == 1):
       host_target = host_dev
       
   
   
   local_db = MySQLdb.connect(
                host=host_target,
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
   
   stoplist = set('for a of the and to in'.split())

   tweets = getTweetOccurances(90, 1, local_db_tweets)
   tweet_array = []
   for tweet in tweets:
      tweet_array.append(tweet["text"])
      
   print tweet_array

   #texts = [[word for word in document.lower().split() if word not in stoplist]
   #for document in documents]