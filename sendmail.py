# -*- encoding:utf-8
'''
Created on 2015年4月10日

@author: SunHongjian
'''

import smtplib #, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from email.mime.image import MIMEImage
username = '邮箱名'
password = '密码'

smtpserver = 'smtp.163.com'
fromaddr = "邮箱全名带@"
toaddr = "目的邮箱全名带@"

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Email for Test"

txt = MIMEText("Email Content")
msg.attach(txt)

smtp = smtplib.SMTP()
smtp.connect(smtpserver)
smtp.login(username, password)
smtp.sendmail(fromaddr, toaddr, msg.as_string())
smtp.quit()
