#email_notifier
#written by Michael Ramm, Haeffner Lab 2/2/2010
#based on http://en.wikibooks.org/wiki/Python_Programming/Email
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import base64
from email.utils import COMMASPACE

class notifier():
	def __init__(self):
		# Credentials
		self.username = 'haeffnerlab'
		self.fromaddr = 'haeffnerlab@gmail.com'
		#uses base64 to provide an illusion of security
		self.password = base64.b64decode("Mzk3ODY2UzEyRDUy")
		self.toaddrs = ''
		self.subject = ''
		self.body = ''
	# sets the email's recepients, should be in form ['user@server.com','user1@server1.com']
	def set_recepients(self,toaddrs):
		self.toaddrs = toaddrs
	def set_content(self,subject, body):
		self.subject = subject
		self.body = body
	def send(self):
		#sends the email
		self.msg = MIMEMultipart()
		self.msg['From'] = self.fromaddr
		self.msg['To'] = COMMASPACE.join(self.toaddrs)
		self.msg['Subject'] = self.subject
		self.msg.attach(MIMEText(self.body, 'plain'))
		self.server = smtplib.SMTP('smtp.gmail.com:587')
		self.server.ehlo()
		self.server.starttls()
		self.server.ehlo()
		self.server.login(self.username,self.password)
		self.server.sendmail(self.fromaddr, self.toaddrs, self.msg.as_string())
		print self.msg.as_string()
		self.server.quit()
	def __del__(self):
		pass
