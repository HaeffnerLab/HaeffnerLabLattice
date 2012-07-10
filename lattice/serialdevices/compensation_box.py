"""
### BEGIN NODE INFO
[info]
name = Compensation Box
version = 1.1
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
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
import binascii
from labrad.server import Signal
from labrad import types as T

PREC_BITS = 16.
DAC_MAX = 2500.
MAX_QUEUE_SIZE = 1000
TIMEOUT = 1.0 #time to wait for response from dc box
RESP_STRING = 'r' #expected response from dc box after write
ERROR_TIME = 1.0 #time to wait if correct response not received

SIGNALID = 94976

class CompensationBox( SerialDeviceServer ):
    name = 'Compensation Box'
    regKey = 'COMPBOX'
    port = None
    serNode = 'lattice-imaging'
    timeout = T.Value(TIMEOUT,'s')
    onNewUpdate = Signal(SIGNALID, 'signal: channel has been updated', '(wv)')

    @inlineCallbacks
    def initServer( self ):
        """
        Initialize server      
        Initializes dictionary (dcDict) of relevant device data
        Initializes queue (queue) for commands to send
        Initializes serial connection
        Frees connection for writing
        @raise SerialDeviceError: (For subclass author) Define regKey and serNode attributes
        """
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
        yield self.populateDict()
        self.listeners = set()
        self.free = True
    
    def createDict( self ):
        """
        Initializes dictionary object (d) in the format
        channel : {'devChannel':
                    'range':
                    'calibration':
        """
        self.d = {
                  1: {'devChannel':0,
                      'range':(-479, -10),
                      }, 
                  2: {'devChannel':1,
                      'range':(-479, -10),
                      } 
                  }
        self.addCalibration()
        
    def addCalibration(self):
        #calibration with two points in the format (channel, (voltage, sequential DAC))
        recordedCalibration = ((1,((-7.67, 2000), (-479.9, 2**16 - 1))), (2,((-7.82, 2000), (-483.3, 2**16 - 1))) ) 
        for chan, points in recordedCalibration:
            m = ( points[1][1] - points[0][1] ) / ( points[1][0] - points [0][0] )
            b = points[0][1] - m * points[0][0]
            self.d[chan]['calibration'] = (m,b)
    
    @inlineCallbacks
    def populateDict(self):
        """
        Gets the information about the current setting from the hardware
        """
        for channel in self.d.keys():
            devChannel = self.d[channel]['devChannel']
            comstring = str(devChannel)+'r'
            yield self.ser.write(comstring)
            encoded = yield self.ser.read(3)
            seq = int(binascii.hexlify(encoded[0:2]),16)
            voltage = self.seqToVoltage(channel, seq)
            self.d[channel]['value'] = voltage

    @inlineCallbacks      
    def tryToSend( self, channel, value ):
        """
        Check if serial connection is free.
        If free, write value to channel.
        If not, store channel and value as tuple in queue.
        Raise error when queue fills up.
        """
        if self.free:
            self.free = False
            yield self.writeToSerial( channel, value )
        elif len( self.queue ) > MAX_QUEUE_SIZE:
            raise Exception( 'Queue size exceeded')
        else: self.queue.append( ( channel, value ) )
        
    @inlineCallbacks
    def writeToSerial( self, channel, value ):
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
        toSend = self.mapMessage( channel, value )   
        self.ser.write( toSend )
        resp = yield self.ser.read( len( RESP_STRING ) )
        if RESP_STRING != resp:
#            Since we didn't get the the correct response,
#            place the value back in the front of the queue
#            and wait for a specified ERROR_TIME before
#            checking the queue again.
            self.queue.insert( 0, ( channel, value ) )
            reactor.callLater( ERROR_TIME, self.checkQueue )
            raise Exception ( 'Correct response from DC box not received, sleeping for short period')
        else:
#            Since we got the correct response,
#            update the value entry for this channel
#            and check the queue.
            self.d[channel]['value'] = value
            self.checkQueue()
    
    @inlineCallbacks
    def checkQueue( self ):
        """
        Check queue for values to write
        """
        if self.queue:
            yield self.writeToSerial( *self.queue.pop( 0 ) )
        else:
            self.free = True

    def validateChannel( self, channel ):
        """
        Check to see if specified device possesses specified channel.
        """
        if channel not in self.d.keys(): raise Exception('Invalid device channel {}'.format(channel))

    def validateVoltage( self, channel, voltage ):
        """
        Check to see if value lies within specified device's range.
        """
        (MIN,MAX) = self.d[channel]['range']
        if not MIN <= voltage <= MAX: raise Exception('Invalid voltage {}'.format(voltage))

    @setting( 0, channel = 'w: which electrode (1 or 2)', voltage = 'v: voltage to apply', returns = '' )
    def setComp( self, c, channel, voltage ):
        """
        Sets compensation electrode voltages.
        """
        self.validateChannel( channel )
        self.validateVoltage( channel, voltage )
        self.tryToSend( channel, voltage )
        self.notifyOtherListeners(c, (channel,voltage))

    @setting( 1 , channel = 'w: which electrode (1 or 2)', returns = 'v: voltage' )
    def getComp( self, c, channel ):
        """
        Retrieve compensation voltage for specified device channel.
        """
        self.validateChannel( channel )
        value = self.d[channel]['value']
        return value
    
    @setting(2,  channel = 'w: which electrode (1 or 2)', returns = '*v: range' )
    def getRange(self, c, channel):
        """
        Returns range of the specified device channel
        """
        self.validateChannel( channel )
        range = self.d[channel]['range']
        return range
    
    def notifyOtherListeners(self, context, chanInfo):
        """
        Notifies all listeners except the one in the given context
        """
        notified = self.listeners.copy()
        notified.remove(context.ID)
        self.onNewUpdate(chanInfo, notified)

    def seqToVoltage(self, channel, seq):
        (m,b) = self.d[channel]['calibration']
        voltage = (seq  - b) / m
        return voltage
    
    def volToSequential(self, channel, voltage):
        (m,b) = self.d[channel]['calibration']
        seq = int(round( m * voltage + b ))
        return seq
    
    def mapMessage( self, channel, value ):
        devChannel = self.d[channel]['devChannel']
        return self.makeComString( devChannel, self.volToSequential( channel, value ) )
    
    #converts sequential representation to string understood by microcontroller                                                                                                        
    #i.e ch 1 set to maximum, which is sequentially 2**16-1 or ffff in hex -> '1,str' where str =  is character representation of 0xffff given by binascii.unhexlify(ffff)
    @staticmethod
    def makeComString( channel, binVolt ):
        hexrepr = hex( binVolt )[2:] #select ffff out of 0xfff'                                                                                                                          
        hexrepr = hexrepr.zfill( 4 ) #left pads to make sure 4 characters                                                                                                            
        numstr = binascii.unhexlify( hexrepr ) #converts ffff to ascii characters                                                                                                    
        comstring = str( channel ) + ',' + numstr
        return comstring
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)

if __name__ == "__main__":
    from labrad import util
    util.runServer( CompensationBox() )