'''
Created on Jan 26, 2011

@author: christopherreilly
'''

from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
import binascii

SERVERNAME = 'LaserDAC'
PREC_BITS = 16.
DAC_MAX = 2500.
MAX_QUEUE_SIZE = 1000
#time to wait for response from dc box
TIMEOUT = 1.0
#expected response from dc box after write
RESP_STRING = 'r'
#time to wait if correct response not received
ERROR_TIME = 1.0

class DCBoxError( SerialConnectionError ):
    errorDict = {
        0:'Invalid device channel',
        1:'Value out of range',
        2:'Queue size exceeded',
        3:'Shutter input must be boolean',
        4:'Must set value before you can retrieve',
        5:'Correct response from DC box not received, sleeping for short period'
        }

class DCBoxServer( SerialDeviceServer ):
    """
    DC Box Server
    
    Serial device controlling three separate functions:
        
        End caps
        Compensation Electrodes
        Shutters
    """
    name = SERVERNAME
    regKey = 'LaserRoomDac'
    port = None
    serNode = 'lab-49'
    timeout = TIMEOUT

    @inlineCallbacks
    def initServer( self ):
        """
        Initialize DC Box server
        
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
            print self.serNode
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
        self.populateDict()
        self.free = True

    def createDict( self ):
        """
        Initializes DC Box dictionary (dcDict)
        Format is as follows:
        
        dcDict = {
            device:{
                devChannels:{
                    devChannel:{
                        channel:(channel value)
                        value:(state of device)
                        }
                    ...
                    }
                range:( (minValue, maxValue) )
                }
            ...
            }
        """
        d = {}
        devTup = ( 'cavity', )
        for dev in devTup:
            d[dev] = {'devChannels':{}}
        cavity = ( ( '397', 0 ), ( '866', 1 ), ('422', 2) )
        chanTup = (cavity,)
        for dev, value in zip( devTup, chanTup ):
            for chanPair in value:
                d[dev]['devChannels'][chanPair[0]] = {'value':None, 'channel':chanPair[1]}
        cavityRange = (0.0,2500.0)
        rangeTup = ( cavityRange,)
        for dev, value in zip( devTup, rangeTup ): d[dev]['range'] = value
        self.dcDict = d
    
    @inlineCallbacks
    def populateDict(self):
        """
        Gets the information about the current setting from the hardware
        """
        for dev in self.dcDict:
            for devChannel in self.dcDict[dev]['devChannels']:
                channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
                comstring = str(channel)+'r'
                yield self.ser.write(comstring)
                encoded = yield self.ser.read(3)
                seq = int(binascii.hexlify(encoded[0:2]),16)
                voltage = int(round(float(seq * DAC_MAX) / (2**16 - 1)))
                self.dcDict[dev]['devChannels'][devChannel]['value'] = voltage
            
    @inlineCallbacks
    def checkQueue( self ):
        """
        When timer expires, check queue for values to write
        """
        if self.queue:
            print 'clearing queue...(%d items)' % len( self.queue )
            yield self.writeToSerial( *self.queue.pop( 0 ) )
        else:
            print 'queue free for writing'
            self.free = True

    def tryToSend( self, channel, value ):
        """
        Check if serial connection is free.
        If free, write value to channel.
        If not, store channel and value as tuple in queue.
        Raise error when queue fills up.
        
        @param channel: Channel to write to
        @param value: Value to write
        
        @raise DCBoxError: Error code 2.  Queue size exceeded
        """
        if self.free:
            self.free = False
            self.writeToSerial( channel, value )
        elif len( self.queue ) > MAX_QUEUE_SIZE:
            raise DCBoxError( 2 )
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
#            Since we didn't get the the correct reponse,
#            place the value back in the front of the queue
#            and wait for a specified ERROR_TIME before
#            checking the queue again.
            self.queue.insert( 0, ( channel, value ) )
            reactor.callLater( ERROR_TIME, self.checkQueue )
            raise DCBoxError(5)
        else:
#            Since we got the correct reponse,
#            update the value entry for this channel
#            and check the queue.
            dev, devChannel = self.getChannelInfo( channel )
            self.dcDict[dev]['devChannels'][devChannel]['value'] = value
            self.checkQueue()

    def validateDevChannel( self, dev, devChannel ):
        """
        Check to see if specified device possesses specified devChannel.
        
        @param dev: DC Box device
        @param devChannel: DC Box device channel
        
        @raise DCBoxError: Error code 0.  Device does not possess devChannel.
        """
        d = self.dcDict
        if devChannel not in d[dev]['devChannels'].keys(): raise DCBoxError( 0 )

    def validateInput( self, dev, value ):
        """
        Check to see if value lies within specified device's range.
        
        @param dev: DC Box device
        @param value: DC Box device value
        
        @raise DCBoxError: Error code 3.  Value not within device's range.
        """
        d = self.dcDict
        MIN, MAX = d[dev]['range']
        if not MIN <= value <= MAX: raise DCBoxError( 1 )


    @setting( 0 , devChannel = 's: which laser (i.e 397 )',
              voltage = 'v: voltage to apply',
              returns = '' )
    def setCavity( self, c, devChannel, voltage ):
        """
        Sets end cap voltage.
        """
        dev = 'cavity'
        self.validateDevChannel( dev, devChannel )
        self.validateInput( dev, voltage )
        channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
        self.tryToSend( channel, voltage )

    @setting( 1 , devChannel = 's: which laser (i.e 397 )',
              returns = 'v: voltage' )
    def getCavity( self, c, devChannel ):
        """
        Retrieve end cap voltage for specified device channel.
        """
        dev = 'cavity'
        self.validateDevChannel( dev, devChannel )
        value = self.dcDict[dev]['devChannels'][devChannel]['value']
        if value is not None: return value
        else: raise DCBoxError( 4 )

       #DAC is 16 bit, so the function accepts voltage in mv and converts it to a sequential representation                                                                               
    #2500 -> 2^16 , #1250 -> 2^15
    @staticmethod
    def voltageToFormat( voltage ):
        return int( ( 2. ** PREC_BITS - 1 ) * voltage / DAC_MAX )

    #converts sequential representation to string understood by microcontroller                                                                                                        
    #i.e ch 1 set 2500mv -> '1,str' where str =  is  character representation of 0xffff given by binascii.unhexlify(ffff)
    @staticmethod
    def makeComString( channel, binVolt ):
        hexrepr = hex( binVolt )[2:] #select ffff out of 0xfff'                                                                                                                          
        hexrepr = hexrepr.zfill( 4 ) #left pads to make sure 4 characters                                                                                                            
        numstr = binascii.unhexlify( hexrepr ) #converts ffff to ascii characters                                                                                                    
        comstring = str( channel ) + ',' + numstr
        return comstring

    def mapMessage( self, channel, value ):
        """
        Map value to serial string for specified channel.
        
        Note that channel is different from device channel.
        
        @param channel: Use channel to determine mapping parameters
        @param value: Value to be converted
        
        @return: value formatted for serial communication
        """
        def mapVoltage( value, range ):
            return ( float( value ) - float( range[0] ) ) * DAC_MAX / ( range[1] - range[0] )
        d = self.dcDict
        dev = self.getChannelInfo( channel )[0]
        range = d[dev]['range']
        if dev == 'shutter': value = range[1] if value else range[0]
        return self.makeComString( channel, self.voltageToFormat( mapVoltage( value, range ) ) )

    def getChannelInfo( self, channel ):
        """
        Retrieve device info from channel
        
        @param channel: DC Box channel
        
        @return: two-tuple of device and device channel assosciated with channel
        """
        d = self.dcDict
        for dev in d:
            for devChannel in d[dev]['devChannels']:
                if d[dev]['devChannels'][devChannel]['channel'] == channel: return ( dev, devChannel )

if __name__ == "__main__":
    from labrad import util
    util.runServer( DCBoxServer() )


