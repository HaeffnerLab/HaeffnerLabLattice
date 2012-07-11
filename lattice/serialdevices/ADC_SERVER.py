"""
### BEGIN NODE INFO
[info]
name = ADCserver
version = 1.1
description = 
instancename = ADCserver

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

#written by Michael Ramm, Haeffner lab, Nov 2011
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet.defer import returnValue
from labrad import types as T

PREC_BITS = 10.
DAC_MAX = 1023.#mV
VOLTAGE_MAX = 2500.0 #mV
RESPLENGTH = 5

class ADCServer( SerialDeviceServer ):
    """
    Server for communication with ADC
    """
    name = 'ADCserver'
    regKey = 'ADC'
    port = None
    serNode = 'lattice-imaging'
    timeout = T.Value(1.0, 's')

    @inlineCallbacks
    def initServer( self ):
        """Initialize ADC Server server"""
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            yield self.initSerial( serStr, port )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise
        self.makeChannelDict()
        
    def makeChannelDict(self):
        self.d = {'1':1,
                  '2':2,
                  '3':3,
                  '4':4,
                  '5':5,
                  '6':6,
                  '7':7,
                  '8':8,
                  '9':9,
                  '397Table':1,
                  '866Table':2,
                  '422Table':3,
                  '397Intensity':6
                  }
    
    @inlineCallbacks
    def getVoltage( self, channel):
        """Get voltage from ADC"""
        self.checkConnection()
        toSend = self.mapQuery( channel  )
        yield self.ser.write( toSend )
        rawVoltage = yield self.ser.read(RESPLENGTH) 
        voltage = self.mapVoltage(rawVoltage)
        returnValue(voltage)

    def mapQuery(self, ch):
        return str(ch)
    
    def mapVoltage(self, rawVoltage):
        voltage = int(VOLTAGE_MAX * ( float(rawVoltage) ) /  DAC_MAX) 
        return voltage
    
    @setting( 0 , channel = 's: channel', returns = 'v: voltage' )
    def measureChannel( self, c, channel):
        """
        Measures the voltage on the given channel
        """
        if channel not in self.d.keys(): raise Exception("Incorrect Channel")
        chanNumber = self.d[channel]
        voltage = yield self.getVoltage(chanNumber)
        returnValue(voltage)

if __name__ == "__main__":
    from labrad import util
    util.runServer( ADCServer() )