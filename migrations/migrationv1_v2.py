#This is a migration from 7a9e15e830e7b82856 to next commit
import MySQLdb

import sys



host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live


def forward():
    
    if(sys.argv[1] == 0):
        host_target = host_live
    elif(sys.argv[1] == 1):
        host_target = host_dev
    
    print "found host target"+host_target   
    global db
    
    db = MySQLdb.connect(
        host=host_target,
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)
