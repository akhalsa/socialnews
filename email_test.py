import smtplib

fromaddr = 'akhalsa43@gmail.com'
toaddrs  = 'akhalsa43@gmail.com'
msg = 'There was a terrible error that occured and I wanted you to know!'


# Credentials (if needed)
username = 'akhalsa43'
password = 'sophiesChoice1'

# The actual mail send
server = smtplib.SMTP_SSL('smtp.gmail.com:465')
server.starttls()
server.login(username,password)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()