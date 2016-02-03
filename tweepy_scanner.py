import MySQLdb
import subprocess
import sys
import time
from tornado.options import define, options, parse_command_line


define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live

MAX_SECONDS_TO_REBOOT = 60

    
    
if __name__ == '__main__':
        
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
    elif(options.mysql_host == 1):
        host_target = host_dev
        
    global db

    global process
    process = None
    
    db = MySQLdb.connect(
        host=host_target,
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)
    
    while True:
        #ok we need to check to make sure the most recent tweet is within the past hour
        cursor =db.cursor()
        sql = "SELECT ID, timestamp, TIMESTAMPDIFF(SECOND, timestamp, NOW()) FROM Tweet ORDER BY timestamp DESC LIMIT 10;"
        cursor.execute(sql)
        shouldReboot = True        
        if cursor.rowcount > 0:
            row = cursor.fetchone()
            tweet_id = row[0]
            tweet_timestamp = row[1]
            tweet_since = row[2]
            if(tweet_since < MAX_SECONDS_TO_REBOOT):
                shouldReboot = False
                
                
        if(shouldReboot):
            if(process is not None):
                process.terminate()
            print "MUST REBOOT"
            process = subprocess.Popen([sys.executable,"tweepy_listener.py","--mysql_host=1"])
            
        time.sleep(60)
        
                    
            
        
        
        