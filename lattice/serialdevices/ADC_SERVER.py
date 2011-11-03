#writetn by Michael Ramm, Haeffner lab, Nov 2011
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet.defer import returnValue

PREC_BITS = 10.
DAC_MAX = 1023.#mV
VOLTAGE_MAX = 2500.#mv
RESPLENGTH = 5

class ADCServer( SerialDeviceServer ):
    """
    Server for communication with ADC
    """
    name = 'ADCserver'
    regKey = 'ADC'
    port = None
    serNode = 'lattice-pc'
    timeout = 1.0

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
        self.possibleChannels = range(1,9)
    
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
    
    @setting( 0 , channel = 'w: channel number', returns = 'v: voltage' )
    def measureChannel( self, c, channel):
        """
        Measures the voltage on the given channel
        """
        if channel not in self.possibleChannels: raise Exception("Incorrect Channel")
        voltage = yield self.getVoltage(channel)
        returnValue(voltage)

if __name__ == "__main__":
    from labrad import util
    util.runServer( ADCServer() )