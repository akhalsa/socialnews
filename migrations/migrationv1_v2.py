#This is a migration from 7a9e15e830e7b82856 to next commit
import MySQLdb

import sys



host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live


def forward():
    print "got sys arg: "+sys.argv[0]+" and second sys arg: "+sys.argv[1]
    
    if(sys.argv[1] == "0"):
        host_target = host_live
    elif(sys.argv[1] == "1"):
        print "got to host_target assignment"
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
