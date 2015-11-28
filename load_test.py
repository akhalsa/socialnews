import pycurl
from StringIO import StringIO
import thread
import time
#load test

#/reader/Sports/time/900


def hitReader():
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'filtra.io:8888/reader/Sports/time/9000')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    
    body = buffer.getvalue()
    # Body is a string in some encoding.
    # In Python 2, we can print it without knowing what the encoding is.
    print(body)
    
    

thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
time.sleep(1)
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
time.sleep(1)
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
time.sleep(1)
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
time.sleep(1)
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
thread.start_new_thread( hitReader, ())
time.sleep(3)