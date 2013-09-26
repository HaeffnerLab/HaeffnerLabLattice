"""
### BEGIN NODE INFO
[info]
name = Agilent 6030A Server
version = 1.0
description = 
instancename = Agilent 6030A Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from common.serialdevices.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from twisted.internet.defer import returnValue, Deferred
from twisted.internet import reactor
from labrad.units import WithUnit
from labrad.server import Signal

class Agilent_6030A( SerialDeviceServer ):
    """
    Server for communication with ADC
    """
    name = 'Agilent 6030A Server'
    regKey = 'Agilent 6030A Server'
    port = None
    serNode = 'lattice_control'
    timeout = WithUnit(1.0, 's')

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
    
    @setting( 0 , voltage = 'v[V]: voltage', returns = 'v[V]: voltage')
    def voltage( self, c, voltage = None):
        """
        Read or set the voltage setpoint
        """
        if voltage is None:
            yield self.ser.write('VSET?\n')
            yield self.ser.write('++read eoi\r\n')
            volt_str = yield self.ser.readline()
            voltage = volt_str[4:].strip()
            voltage = WithUnit(float(voltage), 'V')
        else:
            volt_str = 'VSET{0:.3f}V\n'.format(voltage['V'])
            yield self.ser.write(volt_str)
        returnValue(voltage)
    
    @setting( 1 , current = 'v[A]: current', returns = 'v[A]: current')
    def current( self, c, current = None):
        """
        Read or set the current setpoint
        """
        if current is None:
            yield self.ser.write('ISET?\n')
            yield self.ser.write('++read eoi\r\n')
            current_str = yield self.ser.readline()
            current_str = current_str[4:].strip()
            current = WithUnit(float(current_str), 'A')
        else:
            current_str = 'ISET{0:.3f}A\n'.format(current['A'])
            yield self.ser.write(current_str)
        returnValue(current)
        
if __name__ == "__main__":
    from labrad import util
    util.runServer( Agilent_6030A() )