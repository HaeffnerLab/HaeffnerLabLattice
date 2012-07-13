#Created on Feb 22, 2012
#@author: Hong, Mike Haeffner Lab
'''
### BEGIN NODE INFO
[info]
name = DAC
version = 1.0
description =
instancename = DAC

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
'''
from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.threads import deferToThread
from api_dac import api_dac

class dac_channel(object):
    def __init__(self, name, channel_number, min_voltage, vpp = 20.0, value = None):
        '''min voltage is used to calibrate the offset of the channel'''
        self.name = name
        self.channel = channel_number
        self.min_voltage = min_voltage
        self.max_voltage = min_voltage + vpp
        self.value = value
    
    def is_in_range(self, voltage):
        return (self.min_voltage  <= voltage <= self.max_voltage)
    
    def get_range(self):
        return (self.min_voltage, self.max_voltage)
    
class DAC(LabradServer):
    
    name = 'DAC'
    onNewVoltage = Signal(123556, 'signal: new voltage', '(vv)')
    
    @inlineCallbacks
    def initServer(self):
        self.api_dac  = api_dac()
        self.inCommunication = DeferredLock()
#        connected = self.api_dac.connectOKBoard()
#        if not connected:
#            raise Exception ("Could not connect to DAC")
        self.d = yield self.initializeDAC()
        self.listeners = set()     
    
    @inlineCallbacks
    def initializeDAC(self):
        d = {}
        for name,channel,min_voltage in [
                             ('dconrf1', 0, -9.9558),
                             ('dconrf2', 1, -9.9557),
                             ('endcap1', 2, -9.9552),
                             ('endcap2', 3, -9.9561),
                             ]:
            chan = dac_channel(name, channel, min_voltage)
            chan.value = yield self.getRegValue(name)
            d[name] = chan
        returnValue( d )
    
    @inlineCallbacks
    def getRegValue(self, name):
        yield self.client.registry.cd(['','Servers', 'DAC'], True)
        try:
            voltage = yield self.client.registry.get(name)
        except Exception:
            print '{} not found in registry'.format(name)
            voltage = 0
        returnValue(voltage)
            
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
    
    @inlineCallbacks
    def stopServer(self):
        '''save the latest voltage information into registry'''
        try:
            yield self.client.registry.cd(['','Servers', 'DAC'], True)
            for name,channel in self.d.iteritems():
                yield self.client.registry.set(name, channel.value)
        except AttributeError:
            pass

if __name__ == "__main__":
    from labrad import util
    util.runServer( DAC() )