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
       
   
   finished = False
   
   while(not finished):
      local_db_cats = MySQLdb.connect(
                   host=host_target,
                   user="akhalsa",
                   passwd="sophiesChoice1",
                   db="newsdb",
                   charset='utf8',
                   port=3306)
   
      all_ids = getAllCategoryIds(local_db_cats)
      for cat_id in all_ids:
         
         tweets = getTweetOccurances(900, cat_id, local_db_cats)
         tweet_array = []
         total_count = 0
         for tweet in tweets:
            tweet_array.append(tweet["text"])
            total_count += tweet["tweet_count"]
            
            
            
         if len(tweet_array) < 10:
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
         
         
         lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=4)
         
         corpus_lsi = lsi[corpus_tfidf]
      
         
         for index, elem in enumerate(lsi.projection.s):
            print index
            if(elem > 1.9):
               print "in category: "+str(cat_id)+" we had a trending topic at index: "+str(index)
               trend_count = 0
               included_tweets = []
               for tweet_index, doc in enumerate(corpus_lsi): # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
                  for score_tuple in doc:
                     if(score_tuple[0] == index):
                        if(score_tuple[1] > .8):
                           trend_count += tweets[tweet_index]["tweet_count"]
                           included_tweets.append(tweets[tweet_index])
                           
               
            
            if((trend_count / float(total_count)) > .5):
               finished = True
               print "in category: "+str(cat_id)
               print "we had a tweet cluster: "
               print included_tweets
               
               
         if(finished):
            break
   
            
   
               
                        
            
         
      
      
      
      
      