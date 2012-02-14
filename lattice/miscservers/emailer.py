"""
### BEGIN NODE INFO
[info]
name = Email Server
version = 1.0
description = 
instancename = Email Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.utils import COMMASPACE
import base64

class emailer( LabradServer ):
    name = 'Email Server'
    
    @inlineCallbacks
    def initServer( self ):
        self.username, self.fromaddr, self.password = yield self.getInfoReg()
        self.password = base64.b64decode(self.password)
        self.toaddrs = {}
        self.smtp = 'smtp.gmail.com:587'
        self.sending = DeferredLock()
    
    @inlineCallbacks
    def getInfoReg(self):
        reg = self.client.registry
        yield reg.cd(['Servers','Email Server'])
        username = yield reg.get('username')
        fromaddr = yield reg.get('address')
        password = yield reg.get('password')
        returnValue([username,fromaddr,password])
        
    @setting(0, "Set Recipients", recepients = '*s', returns = '')
    def setRecepients(self, c, recepients):
        """Set the recipients of the email as a list of strings of email addresses"""
        self.toaddrs[c.ID] = recepients
    
    @setting(1, "Send", subject = 's', message = 's', returns = '')
    def selectDP(self, c, subject, message):
        """Select Double Pass in the current context"""
        if not self.toaddrs[c.ID]: raise Exception("Recipients not set")
        yield self.sending.acquire()  
        session = smtplib.SMTP(self.smtp)
        session.starttls()
        session.login(self.username,self.password)
        toaddrs = self.toaddrs[c.ID]
        msg = MIMEMultipart()
        msg['From'] = self.fromaddr
        msg['To'] = COMMASPACE.join(toaddrs)
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))    
        session.sendmail(self.fromaddr, toaddrs, msg.as_string())
        session.quit()
        self.sending.release()
    
    def initContext(self, c):
        """Initialize a new context object."""
        pass
    
    def expireContext(self, c):
        del(self.toaddrs[c.ID])
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(emailer())
