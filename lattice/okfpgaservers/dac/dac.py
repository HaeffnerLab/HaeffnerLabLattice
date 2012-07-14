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
from labrad import types as T
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.threads import deferToThread
from api_dac import api_dac

class dac_channel(object):
    def __init__(self, name, channel_number, min_voltage, vpp = 20.0, voltage = None):
        '''min voltage is used to calibrate the offset of the channel'''
        self.name = name
        self.channel_number = channel_number
        self.min_voltage = min_voltage
        self.max_voltage = min_voltage + vpp
        self.vpp = vpp
        self.voltage = voltage
    
    def is_in_range(self, voltage):
        return (self.min_voltage  <= voltage <= self.max_voltage)
    
    def get_range(self):
        return (self.min_voltage, self.max_voltage)
    
class DAC(LabradServer):
    
    name = 'DAC'
    onNewVoltage = Signal(123556, 'signal: new voltage', '(sv)')
    
    @inlineCallbacks
    def initServer(self):
        self.api_dac  = api_dac()
        self.inCommunication = DeferredLock()
        connected = self.api_dac.connectOKBoard()
        if not connected:
            raise Exception ("Could not connect to DAC")
        self.d = yield self.initializeDAC()
        self.listeners = set()     
    
    @inlineCallbacks
    def initializeDAC(self):
        '''creates dictionary for information storage'''
        d = {}
        for name,channel_number,min_voltage in [
                             ('dconrf1', 0, -9.9558),
                             ('dconrf2', 1, -9.9557),
                             ('endcap1', 2, -9.9552),
                             ('endcap2', 3, -9.9561),
                             ]:
            chan = dac_channel(name, channel_number, min_voltage)
            chan.voltage = yield self.getRegValue(name)
            d[name] = chan
            value = self.voltage_to_val(chan.voltage, chan.min_voltage, chan.vpp)
            yield self.do_set_voltage(channel_number, value)
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
            
    @setting(0, "Set Voltage",channel = 's', voltage = 'v[V]', returns = '')
    def setVoltage(self, c, channel, voltage):
        try:
            chan = self.d[channel]
            minim,total,channel_number = chan.min_voltage, chan.vpp, chan.channel_number
        except KeyError:
            raise Exception ("Channel {} not found".format(channel))
        voltage = voltage['V']
        value = self.voltage_to_val(voltage, minim, total)
        yield self.do_set_voltage(channel_number, value)
        chan.voltage = voltage
        self.notifyOtherListeners(c, (channel, voltage), self.onNewVoltage)
    
    @inlineCallbacks
    def do_set_voltage(self, channel_number, value):
        yield self.inCommunication.acquire()
        try:
            yield deferToThread(self.api_dac.setVoltage, channel_number, value)
        finally:
            self.inCommunication.release()
        
    
    def voltage_to_val(self, voltage, minim, total, prec = 16):
        '''converts voltage of a channel to FPGA-understood sequential value'''
        value = int((voltage - minim) / total * (2 ** prec  - 1) )
        if not  0 <= value <= 2**16 - 1: raise Exception ("Voltage Out of Range")
        return value
           
    @setting(1, "Get Voltage", channel = 's', returns = 'v[V]')
    def getVoltage(self, c, channel):
        try:
            voltage = self.d[channel].voltage
        except KeyError:
            raise Exception ("Channel {} not found".format(channel))
        return T.Value(voltage, 'V')
    
    @setting(2, "Get Range", channel = 's', returns = '(v[V]v[V])')
    def getRange(self, c, channel):
        try:
            chan = self.d[channel]
            minim,maxim = chan.min_voltage,chan.max_voltage
        except KeyError:
            raise Exception ("Channel {} not found".format(channel))
        return (T.Value(minim,'V'), T.Value(maxim), 'V')
    
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
                yield self.client.registry.set(name, channel.voltage)
        except AttributeError:
            #if dictionary doesn't exist yet (i.e bad identification error), do nothing
            pass

if __name__ == "__main__":
    from labrad import util
    util.runServer( DAC() )