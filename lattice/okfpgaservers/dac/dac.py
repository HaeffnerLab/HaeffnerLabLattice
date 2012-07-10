#Created on Feb 22, 2012
#@author: Hong, Haeffner Lab

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock, Deferred
from twisted.internet.threads import deferToThread
from api_dac import api_dac

class DAC(LabradServer):
    name = 'DAC'
    
    def initServer(self):
    	self.api_dac  = api_dac()
        self.inCommunication = DeferredLock()
        self.initializeBoard()
        self.initializeSettings()
        self.listeners = set()   ### what is this?

    def initializeBoard(self):
        connected = self.api_dac.connectOKBoard()
        while not connected:
            print 'not connected, waiting for 10 seconds to try again'
            self.wait(10.0)
            connected = self.api_dac.connectOKBoard()
            
    def initializeSettings(self):
    	##### read channel values #####
    	
    def wait(self, seconds, result=None):
        """Returns a deferred that will be fired later"""
        d = Deferred()
        reactor.callLater(seconds, d.callback, result)
        return d
    
    def cnot(self, control, input):
        if control:
            input = not input
        return input
    
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