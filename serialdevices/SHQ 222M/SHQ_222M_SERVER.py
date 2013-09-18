"""
### BEGIN NODE INFO
[info]
name = SHQ_222M_SERVER
version = 1.0
description = 
instancename = SHQ_222M_SERVER

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
#written by Michael Ramm, Haeffner lab, Nov 2011
from common.serialdevices.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from twisted.internet.defer import returnValue, Deferred
from twisted.internet import reactor
from labrad.units import WithUnit
from labrad.server import Signal

CHANNELS = 2
VOLTAGE_MIN = WithUnit(0, 'V')
VOLTAGE_MAX = WithUnit(2000, 'V')
RAMP = 20 #Volts / sec

class SHQ_222M( SerialDeviceServer ):
    """
    Server for communication with ADC
    """
    name = 'SHQ_222M_SERVER'
    regKey = 'SHQ_222M_SERVER'
    port = None
    serNode = 'lattice_control'
    timeout = WithUnit(1.0, 's')
    
    onNewVoltage = Signal(564867, 'signal: new voltage', '(wv)')

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
        self.listeners = set()
        yield self.initDevice()
    
    @inlineCallbacks
    def initDevice(self):
        yield self.set_auto_start()
        yield self.set_ramp_speed()
            
    @inlineCallbacks
    def set_auto_start(self):
        '''
        enable auto start for both channels. makes voltage change immediately when it's set.
        '''
        for channel in range(1, CHANNELS + 1):
            set_str, expected_response = self._auto_start_str(channel)
            yield self.ser.write(set_str)
            resp_0 = yield self.ser.readline()
            resp_1 = yield self.ser.readline()
            assert (resp_0,resp_1) == expected_response, "Incorrect Response"
    
    @inlineCallbacks
    def set_ramp_speed(self):
        '''
        sets the ramp speed on both channels to the default value
        '''
        for channel in range(1, CHANNELS + 1):
            set_str, expected_response = self._set_ramp_speed_str(channel, RAMP)
            yield self.ser.write(set_str)
            resp_0 = yield self.ser.readline()
            resp_1 = yield self.ser.readline()
            assert (resp_0,resp_1) == expected_response, "Incorrect Response"
    
    @setting( 0 , channel = 'w: channel', voltage = 'v[V]: voltage', returns = 'v[V]: voltage')
    def voltage( self, c, channel, voltage = None):
        """
        Read or set the voltage setpoint on a given channel
        """
        if not channel in range(1, CHANNELS + 1):
            raise Exception ("Incorrect channel")
        if voltage is not None:
            if not (VOLTAGE_MIN <= voltage and voltage <= VOLTAGE_MAX):
                raise Exception ("Voltage out of range")
            send, expected_response = self._set_voltage_str(channel, voltage['V'])
            yield self.ser.write(send)
            resp_0 = yield self.ser.readline()
            resp_1 = yield self.ser.readline()
            assert (resp_0,resp_1) == expected_response, "Incorrect Response"   
            self.notifyOtherListeners(c, (channel, voltage), self.onNewVoltage)    
        else:
            #reading voltage
            send, expected_response = self._get_voltage_str(channel)
            yield self.ser.write(send)
            resp_0 = yield self.ser.readline()
            voltage = yield self.ser.readline()
            assert resp_0 == expected_response, "Incorrect Response"
            mantisee,exponent = int(voltage[:5]),int(voltage[5:])
            voltage = WithUnit(mantisee * 10**exponent, 'V')
        returnValue(voltage)
    
    @setting(1, returns = '(v[V],v[V]): voltage range')
    def voltage_range(self, c):
        return((VOLTAGE_MIN,VOLTAGE_MAX))
    
    @setting(2, channel = 'w: channel', returns = 'v[V]: actual voltage')
    def get_actual_voltage(self, c, channel):
        '''
        get the currently applied voltage on the given channel
        '''
        if not channel in range(1, CHANNELS + 1):
            raise Exception ("Incorrect channel")
        send, expected_response = self._get_actual_voltage_str(channel)
        yield self.ser.write(send)
        resp_0 = yield self.ser.readline()
        voltage = yield self.ser.readline()
        mantisee,exponent = int(voltage[:6]),int(voltage[6:])
        voltage = WithUnit(mantisee * 10**exponent, 'V')
        returnValue(voltage)
    
    @setting(3, channel = 'w: channel', set_point = 'v[V]', precision = 'v[V]', timeout = 'v[s]', returns = 'b')
    def wait_to_be_set(self, c, channel, set_point, precision = None, timeout = None):
        '''
        wait for the specified channel to ramp to the given set_point within the provided precision
        '''
        if not channel in range(1, CHANNELS + 1):
            raise Exception ("Incorrect channel")
        current_voltage = yield self.get_actual_voltage(c, channel)
        if timeout is None: 
            timeout = max(10, (2 * current_voltage['V'] - set_point['V']) / RAMP) #reasonable guess for the ramp time in seconds
        else:
            timeout = timeout['s']
        if precision is None:
            precision = WithUnit(0.5, 'V')
        on_timeout = Deferred()
        reactor.callLater(timeout, on_timeout.callback, True)
        while not on_timeout.called:
            current_voltage = yield self.get_actual_voltage(c, channel)
            yield self.wait(0.1)
            if abs(current_voltage['V'] - set_point['V']) < precision['V']:
                returnValue(True)
        returnValue(False)
        
    def _auto_start_str(self, channel):
        '''
        returns
        set_str, expected_response
        '''
        return 'A{}=8\r\n'.format(channel), ('A{}=8'.format(channel), '')
    
    def _get_voltage_str(self, channel):
        '''
        returns the set voltage
        '''
        return 'D{}\r\n'.format(channel), 'D{}'.format(channel)
    
    def _get_actual_voltage_str(self, channel):
        '''
        returns the actual voltage of the device
        '''
        return 'U{}\r\n'.format(channel), 'U{}'.format(channel)
    
    def _set_voltage_str(self, channel, voltage):
        return 'D{0}={1:07.2f}\r\n'.format(channel, voltage), ('D{0}={1:07.2f}'.format(channel, voltage),'')
    
    def _set_ramp_speed_str(self, channel, ramp):
        return  'V{0}={1:03d}\r\n'.format(channel, ramp), ('V{0}={1:03d}'.format(channel, ramp),'')
    
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
    util.runServer( SHQ_222M() )