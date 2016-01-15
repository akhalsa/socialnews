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
       
   
   
   local_db = MySQLdb.connect(
                host=host_target,
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
   
   stoplist = set('for a of the and to in at an is he her see has'.split())

   tweets = getTweetOccurances(900, 100, local_db)
   tweet_array = []
   for tweet in tweets:
      tweet_array.append(tweet["text"])
      
   print tweet_array

   texts = [[word for word in document.lower().split() if len(word) > 4] for document in tweet_array]
      
   frequency = defaultdict(int)
   for text in texts:
      for token in text:
         frequency[token] += 1
         
   texts = [[token for token in text if frequency[token] > 1] for text in texts]
   
   pprint(texts)
   
   dictionary = corpora.Dictionary(texts)
   
   print(dictionary)
   
   print(dictionary.token2id)
   
   corpus = [dictionary.doc2bow(text) for text in texts]
   
   print(corpus)
   
   tfidf = models.TfidfModel(corpus)
   
   corpus_tfidf = tfidf[corpus]
   
   lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=4)
   
   corpus_lsi = lsi[corpus_tfidf]
   
   lsi.print_topics(4)
   
   for doc in corpus_lsi: # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
      print(doc)