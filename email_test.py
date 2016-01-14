import smtplib

fromaddr = 'filtrasports@gmail.com'
toaddrs  = 'akhalsa43@gmail.com'
msg = 'There was a terrible error that occured and I wanted you to know!'


# Credentials (if needed)
username = 'filtrasports'
password = 'filtra123'

# The actual mail send
server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
server.login(username,password)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()