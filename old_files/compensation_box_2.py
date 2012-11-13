"""
### BEGIN NODE INFO
[info]
name = Compensation Box
version = 1.2
description = 
instancename = Compensation Box

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError
from twisted.internet import reactor
import binascii
from labrad.server import Signal
from labrad.types import Error
from labrad import types as T

PREC_BITS = 16.
DAC_MAX = 2500.
MAX_QUEUE_SIZE = 1000
TIMEOUT = 1.0 #time to wait for response from dc box
RESP_STRING = 'r' #expected response from dc box after write
ERROR_TIME = 1.0 #time to wait if correct response not received
MAX_ERROR_COUNT = 3 #tolerance for consecutive send/receive errors

SIGNALID = 94976

class compensation_channel():
    def __init__(self, name, device_channel, limits, calibration = (1.0, 0.0)):
        self.name = name
        self.channel = device_channel
        self.limits = limits
        self.calibration = calibration
        self._value = None
    
    def setValue(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value
    
    @property
    def comstring(self):
        seq =  self.volToSequential(self._value)
        comstring = self.makeComString(seq)
        return comstring
    
    def volToSequential(self, voltage):
        (m,b) = self.calibration
        seq = int(round( m * voltage + b ))
        return seq
    
    #converts sequential representation to string understood by microcontroller                                                                                                        
    #i.e ch 1 set to maximum, which is sequentially 2**16-1 or ffff in hex -> '1,str' where str =  is character representation of 0xffff given by binascii.unhexlify(ffff)
    def makeComString(self, binVolt ):
        hexrepr = hex( binVolt )[2:] #select ffff out of 0xfff'                                                                                                                          
        hexrepr = hexrepr.zfill( 4 ) #left pads to make sure 4 characters                                                                                                            
        numstr = binascii.unhexlify( hexrepr ) #converts ffff to ascii characters                                                                                                    
        comstring = str( self.channel ) + ',' + numstr
        return comstring
                

class CompensationBox( SerialDeviceServer ):
    name = 'Compensation Box'
    regKey = 'COMPBOX'
    port = None
    serNode = 'lattice_control'
    timeout = T.Value(TIMEOUT,'s')
    onNewUpdate = Signal(SIGNALID, 'signal: channel has been updated', '(sv)')

    @inlineCallbacks
    def initServer( self ):
        self.createDict()
        self.queue = []
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port )
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
        self.error_count = 0
        self.free = True
        yield self.getRegValues()
    
    def createDict( self ):
        """
        Initializes dictionary object (d) with the channel information
        """
        self.d = {}
        self.d['comp1'] = compensation_channel('comp1', 0, (-479.0, -10.0))
        self.d['comp2'] = compensation_channel('comp2', 1, (-479.0, -10.0))
        self.addCalibration()
        
    def addCalibration(self):
        #calibration with two points in the format (channel, (voltage, sequential DAC))
        recordedCalibration = {'comp1':((-7.67, 2000), (-479.9, 2**16 - 1)),
                               'comp2':((-7.82, 2000), (-483.3, 2**16 - 1))
                               } 
        for name, points in recordedCalibration.iteritems():
            m = ( points[1][1] - points[0][1] ) / ( points[1][0] - points [0][0] )
            b = points[0][1] - m * points[0][0]
            self.d[name].calibration = (m,b)
    
    @inlineCallbacks
    def getRegValues(self):
        """
        Gets the information about the current setting from the registry
        """  
        yield self.client.registry.cd(['','Servers', 'Compensation'], True)
        for name,channel in self.d.iteritems():
            try:
                voltage = yield self.client.registry.get(name)
            except Error,e:
                if e.code == 21:
                    print '{} not found in registry'.format(name)
                    r1,r2 = channel.limits
                    first = abs(r1) < abs(r2)
                    if first:
                        voltage = r1
                    else:
                        voltage = r2
                    print 'initializing to value {}'.format(voltage)
                else:
                    raise
            else:
                channel.setValue(voltage)
                message = channel.comstring
                print channel.name, channel.value
                yield self.tryToSend( message )

    @inlineCallbacks      
    def tryToSend( self, message ):
        """
        Check if serial connection is free.
        If free, write value to channel.
        If not, store channel and value as tuple in queue.
        Raise error when queue fills up.
        """
        if self.free:
            self.free = False
            yield self.writeToSerial( message )
        elif len( self.queue ) > MAX_QUEUE_SIZE:
            raise Exception( 'Queue size exceeded')
        else: self.queue.append( message )
        
    @inlineCallbacks
    def writeToSerial( self, message ):
        """
        Write value to specified channel through serial connection.
        
        Convert message to microcontroller's syntax.
        Check for correct response.
        Handle possible error, or
        save written value to memory and check queue.
        
        @param channel: Channel to write to
        @param value: Value to write
        
        @raise SerialConnectionError: Error code 2.  No open serial connection.
        """
        self.checkConnection()
        self.ser.write( message )
        resp = yield self.ser.read( len( RESP_STRING ) )
        if RESP_STRING != resp:
#            Since we didn't get the the correct response,
#            place the value back in the front of the queue
#            and wait for a specified ERROR_TIME before
#            checking the queue again.
            if self.error_count > MAX_ERROR_COUNT:
                raise Exception ("Too many communciation errors")
            self.queue.insert( 0, message )
            self.error_count += 1
            reactor.callLater( ERROR_TIME, self.checkQueue )
            print 'Correct response from DC box not received, sleeping for short period'
        else:
            #got the correct response, clear the erros, moving on
            self.error_count = 0
            self.checkQueue()
    
    @inlineCallbacks
    def checkQueue( self ):
        """
        Check queue for values to write
        """
        if self.queue:
            yield self.writeToSerial( self.queue.pop( 0 ) )
        else:
            self.free = True

    def validateChannel( self, name ):
        """
        Check to see if specified device possesses specified channel.
        """
        if name not in self.d.keys(): raise Exception('Invalid device channel {}'.format(name))

    def validateVoltage( self, name, voltage ):
        """
        Check to see if value lies within specified device's range.
        """
        channel = self.d[name]
        (MIN,MAX) = channel.limits
        if not MIN <= voltage <= MAX: raise Exception('Invalid voltage {}'.format(voltage))

    @setting( 0, name = 's: channel name', voltage = 'v: voltage to apply', returns = '' )
    def setComp( self, c, name, voltage ):
        """
        Sets compensation electrode voltages.
        """
        self.validateChannel( name )
        self.validateVoltage( name, voltage )
        channel = self.d[name]
        channel.setValue(voltage)
        message = channel.comstring
        self.tryToSend( message )
        self.notifyOtherListeners(c, (name,voltage))

    @setting( 1 , name = 's: channel name', returns = 'v: voltage' )
    def getComp( self, c, name ):
        """
        Retrieve compensation voltage for specified device channel.
        """
        self.validateChannel( name )
        value = self.d[name].value
        return value
    
    @setting(2,  name = 's: channel name', returns = '*v: range' )
    def getRange(self, c, name):
        """
        Returns range of the specified device channel
        """
        self.validateChannel( name )
        limits = self.d[name].limits
        return limits
    
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
        
    @inlineCallbacks
    def stopServer(self):
        '''save the latest voltages into registry'''
        try:
            yield self.client.registry.cd(['','Servers', 'Compensation'], True)
            for name,channel in self.d.iteritems():
                yield self.client.registry.set(name, channel.value)
        except AttributeError:
            #if dictionary doesn't exist yet (i.e bad identification error), do nothing
            pass

if __name__ == "__main__":
    from labrad import util
    util.runServer( CompensationBox() )