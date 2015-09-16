import pycurl

#load test

#/reader/Sports/time/900

buffer = StringIO()
c = pycurl.Curl()
c.setopt(c.URL, 'www.cnn.com')
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()

body = buffer.getvalue()
# Body is a string in some encoding.
# In Python 2, we can print it without knowing what the encoding is.
print(body)