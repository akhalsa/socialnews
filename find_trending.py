import MySQLdb
from tornado.options import define, options, parse_command_line
from gensim import corpora, models, similarities
from collections import defaultdict
from pprint import pprint
from src.DBWrapper import *
from src.TrendingWrapper import *

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
   
   lsi_list = []
   
   
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
         
         tweets = getTweetOccurances(1800, cat_id, local_db_cats)
         tweet_array = []
         total_count = 0
         for tweet in tweets:
            ##first check if this works against any existing dictionary/corpus values
            matched = False
            if(inConversation(local_db_cats, tweet)):
               matched = True
            else:
               for model in lsi_list:
                  vec_bow = model["dictionary"].doc2bow(tweet["text"].lower().split())
                  vec_lsi = model["lsi"][vec_bow]
                  for val_tuple in vec_lsi:
                     if(val_tuple[0] == model["index"]):
                        if(val_tuple[1] > 1.5):
                           print "adding: "+tweet["text"]
                           print "to conversation: "+str(model["conversation_id"])+" with score: "+str(val_tuple)
                           addTweetToConversation(local_db_cats, tweet, model["conversation_id"])
                           matched = True
                           break
                  else:
                     continue
            
            if(not matched):
               ##for now lets assume there are none, we will come back
               tweet_array.append(tweet)
            
            
            
         if len(tweet_array) < 10:
            continue
         
         texts = [[word for word in document["text"].lower().split() if len(word) > 4] for document in tweet_array]
         
         frequency = defaultdict(int)
         for text in texts:
            for token in text:
               frequency[token] += 1
               
         texts = [[token for token in text if frequency[token] > 1] for text in texts]
         
         print "checking texts length it was: "+str(len(texts))
         if len(texts) < 6:
            continue
         
         dictionary = corpora.Dictionary(texts)
         
         print "checking dictionary length it was: "+str(len(dictionary))
         if len(dictionary) < 6:
            continue
   
         corpus = [dictionary.doc2bow(text) for text in texts]
   
         tfidf = models.TfidfModel(corpus)
         
         corpus_tfidf = tfidf[corpus]
         
         
         lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=4)
         
         corpus_lsi = lsi[corpus_tfidf]
      
         
         for index, elem in enumerate(lsi.projection.s):
            print index
            if(elem > 1.8):
               
               print "in category: "+str(cat_id)+" we had a trending topic at index: "+str(index)
               trend_count = 0
               included_tweets = []
               max_tweet = None
               handles = {}
               for tweet_index, doc in enumerate(corpus_lsi): # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
                  for score_tuple in doc:
                     if(score_tuple[0] == index):
                        if(score_tuple[1] > .9):
                           trend_count += tweet_array[tweet_index]["tweet_count"]
                           included_tweets.append(tweet_array[tweet_index])
                           handles[tweet_array[tweet_index]["name"]] = True
                           
                           if(max_tweet == None) or (tweet_array[tweet_index]["tweet_count"] > max_tweet["tweet_count"]):
                              max_tweet = tweet_array[tweet_index]
                           
               
            
               if( len(handles) >= 2):
                  print "in category: "+str(cat_id)
                  print "representative tweet: "
                  print max_tweet
                  
                  print "it was in cluster: "
                  print included_tweets
                  conversation_id = addNewConversation(local_db_cats, max_tweet)
                  
                  for tweet in included_tweets:
                     addTweetToConversation(local_db_cats, tweet, conversation_id)
                     
                  lsi_list.append({"lsi": lsi, "index": index, "conversation_id":conversation_id, "dictionary":dictionary})
                  
               else:
                  print str(len(handles))+" in cat id: "+str(cat_id)
                  
              
   
            
   
               
                        
            
         
      
      
      
      
      