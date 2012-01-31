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

from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import base64
from email.utils import COMMASPACE

class emailer( LabradServer ):
    name = 'Email Server'
    
    def initServer( self ):
        self.username = 'haeffnerlab'
        self.fromaddr = 'haeffnerlab@gmail.com'
        self.password = base64.b64decode("Mzk3ODY2UzEyRDUy") #uses base64 to provide an illusion of security
        self.toaddrs = ''
        self.subject = ''
        self.body = ''
        
    def createDict(self):
        self.d = {'axial':axialDP('axial',self.client, self.client.context()),
                  'radial':radialDP('radial',self.client, self.client.context()),
                  'repump':repumpDP('repump',self.client, self.client.context())
                  }
        
    @setting(0, "Get Double Pass List", returns = '*s')
    def getDPList(self, c,):
        """Returns the list of available double passes"""
        return self.d.keys()
    
    @setting(1, "Select", name = 's', returns = '')
    def selectDP(self, c, name):
        """Select Double Pass in the current context"""
        if name not in self.d.keys(): raise Exception("No such double pass")
        c['doublePass'] = self.d[name]
    
    @setting(2, "Frequency", freq ='v', returns = 'v')
    def frequency(self, c, freq = None):
        """Sets the frequency of the selected double pass, returns set frequency"""
        dp = self.getDP(c)
        setfreq = yield dp.frequency(freq)
        if freq is not None: self.notifyOtherListeners(c, (dp.name,'frequency',setfreq))
        returnValue( setfreq )

    @setting(3, "Frequency Calibrated Amplitude", freq = 'v', returns = '(vv)')
    def freqCalibPower(self, c, freq):
        dp = self.getDP(c)
        (setfreq, setamplitude) = yield dp.frequencyCalibPower(freq)
        self.notifyOtherListeners(c, (dp.name,'frequency',setfreq))
        self.notifyOtherListeners(c, (dp.name,'amplitude',setamplitude))
        returnValue( (setfreq, setamplitude) )
        
    @setting(4, "Amplitude", amplitude = 'v', returns ='v')
    def amplitude(self, c, amplitude = None):
        """Sets the amplitude of the selected double pass, returns set amplitude"""
        dp = self.getDP(c)
        setamplitude = yield dp.amplitude(amplitude)
        if amplitude is not None: self.notifyOtherListeners(c, (dp.name,'amplitude',setamplitude))
        returnValue( setamplitude )
    
    @setting(5, "Amplitude Offset", offset = 'v', returns = '(vv)')
    def amplitudeOffset(self, c, offset):
        """Sets the difference between the desired power and the maximum power available from the calibration"""
        if offset > 0: raise Exception ("offset must be negatve")
        dp = self.getDP(c)
        (setoffset,setamplitude) = yield dp.amplitudeOffset(offset)
        if offset is not None: self.notifyOtherListeners(c, (dp.name,'amplitude',setamplitude))
        returnValue( (setoffset,setamplitude) )
    
    @setting(6, "Output", output = 'b', returns = 'b')
    def output(self, c, output = None):
        """Sets the output to true/false for the desired double pass"""
        dp = self.getDP(c)
        setoutput = yield dp.output(output)
        if output is not None: self.notifyOtherListeners(c, (dp.name,'output',setoutput))
        returnValue( setoutput )
    
    @setting(7, "Frequency Range", returns = '(vv)')
    def freqRange(self, c):
        """Returns the frequency range in the current context"""
        dp = self.getDP(c)
        return dp.freqRange
    
    @setting(8, "Amplitude Range", returns = '(vv)')
    def amplRange(self, c):
        """Returns the frequency range in the current context"""
        dp = self.getDP(c)
        return dp.amplRange
    
    def getDP(self, context):
        if not 'doublePass' in context.keys(): raise Exception ('Double Pass not selected')
        return context['doublePass']
    
    def notifyOtherListeners(self, context, chanInfo):
        """
        Notifies all listeners except the one in the given context
        """
        notified = self.listeners.copy()
        notified.remove(context.ID)
        self.onNewUpdate(chanInfo, notified)
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(emailer())
