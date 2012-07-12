#Created on Feb 22, 2012
#@author: Hong, Haeffner Lab

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock, Deferred
from twisted.internet.threads import deferToThread
from api_dac import api_dac

class DAC(LabradServer):
    name = 'DAC'
    onNewVoltage = Signal(123556, 'signal: new voltage', '(vv)')
    
    def initServer(self):
    	self.api_dac  = api_dac()
        self.inCommunication = DeferredLock()
        self.initializeBoard()
        self.listeners = set()

    def initializeBoard(self):
        connected = self.api_dac.connectOKBoard()
        while not connected:
            print 'not connected, waiting for 10 seconds to try again'
            self.wait(10.0)
            connected = self.api_dac.connectOKBoard()       
            
    @setting(0, "Set Voltage",channel = 'i', voltage = 'v', returns = '')
    def setVoltage(self, c, channel, voltage):
        #### calibration for each channel ####
        if (channel == 0):
            value = int((voltage + 9.9558)*2**16/20.0)
        elif (channel == 1):
            value = int((voltage + 9.9557)*2**16/20.0)
        elif (channel == 2):
            value = int((voltage + 9.9552)*2**16/20.0)
        elif (channel == 3):
            value = int((voltage + 9.9561)*2**16/20.0)
        #### set the limit #####    
        if (value>65535):
            value = 65535
            print 'Voltage too high'
        elif (value < 0):
            value = 0
            print 'Voltage too low'
        
        yield self.inCommunication.acquire()
        yield deferToThread(self.api_dac.setVoltage, channel, value)
        self.inCommunication.release()
        self.notifyOtherListeners(c, (channel, value), self.onNewVoltage)
        
    @setting(1, "Get Voltage", channel = 'i', returns = 'v')
    def getVoltage(self, c, channel):
        readout = yield deferToThread(self.api_dac.getVoltage, channel)
        returnValue(readout)
 
    def wait(self, seconds, result=None):
        """Returns a deferred that will be fired later"""
        d = Deferred()
        reactor.callLater(seconds, d.callback, result)
        return d
    
    def notifyOtherListeners(self, context, message, f):
        """
        Notifies all listeners except the one in the given context, executing function f
        """
        notified = self.listeners.copy()
        notified.remove(context.ID)
        f(message,notified)
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)

if __name__ == "__main__":
    from labrad import util
    util.runServer( DAC() )