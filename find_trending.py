import MySQLdb
from tornado.options import define, options, parse_command_line
from gensim import corpora, models, similarities
from collections import defaultdict
from pprint import pprint
from src.DBWrapper import *

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
       
   
   
   local_db_cats = MySQLdb.connect(
                host=host_target,
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)

   all_ids = getAllCategoryIds(local_db_cats)
   for cat_id in all_ids:
      print "checking cat_id "+str(cat_id)
      tweets = getTweetOccurances(900, cat_id, local_db_cats)
      tweet_array = []
      for tweet in tweets:
         tweet_array.append(tweet["text"])
         print "appending: "+tweet["name"]
         
         
      if len(tweet_array) == 0:
         continue
      texts = [[word for word in document.lower().split() if len(word) > 4] for document in tweet_array]
         
      frequency = defaultdict(int)
      for text in texts:
         for token in text:
            frequency[token] += 1
            
      texts = [[token for token in text if frequency[token] > 1] for text in texts]
      
      dictionary = corpora.Dictionary(texts)

      corpus = [dictionary.doc2bow(text) for text in texts]

      tfidf = models.TfidfModel(corpus)
      
      corpus_tfidf = tfidf[corpus]
      
      topic_num = min(len(tweet_array), 4)
      lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=topic_num)
      
      corpus_lsi = lsi[corpus_tfidf]
   
      
      for index, elem in enumerate(lsi.projection.s):
         print index
         if(elem > 2):
            print "in category: "+cat_id+" we had a trending category at index: "+index
            for doc in corpus_lsi: # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
               for thing in doc:
                  print thing
            
         
      
      
      
      
      