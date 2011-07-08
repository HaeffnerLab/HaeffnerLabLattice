'''
Created on Jan 26, 2011

@author: christopherreilly
'''

#===============================================================================
# TODO: Comment thoroughly
#===============================================================================

from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor

import binascii

SERVERNAME = 'DC Box'
PREC_BITS = 16.
DAC_MAX = 2500.
MAX_QUEUE_SIZE = 1000
WAIT_TIME = .05

class DCBoxError( SerialConnectionError ):
    errorDict = {
        0:'Invalid device channel',
        1:'Value out of range',
        2:'Queue size exceeded',
        3:'Shutter input must be boolean'
        }

class DCBoxServer( SerialDeviceServer ):
    """
    DC Box Server
    
    TODO: Description
    """
    name = SERVERNAME
    regKey = 'DCBOX'
    port = None
    serNode = 'lattice-pc'

    waitTime = WAIT_TIME

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
        self.free = True
        self.setComp( None, 'common', 0.0 )

    def createDict( self ):
        d = {}
        devTup = ( 'endcap', 'comp', 'shutter','397intensity' )
        for dev in devTup:
            d[dev] = {'devChannels':{}}
        endcap = ( ( 1, 1 ), ( 2, 0 ) )
        comp = ( ( 1, 4 ), ( 2, 2 ), ( 'common', 3 ) )
        shutter = ( ( 1, 5 ), ( 2, 6 ), ( 3, 7 ) )
        intensity397 = (('397intensity',8),)
        chanTup = ( endcap, comp, shutter ,intensity397 )
        for dev, value in zip( devTup, chanTup ):
            for chanPair in value:
                d[dev]['devChannels'][chanPair[0] ] = {'value':None, 'channel':chanPair[1]}
        ecRange = ( 0.0, 40.0 )
        compRange = ( -18.0, 18.0 )
        shutterRange = ( 0.0, 5.0 )
        intensity397Range = (0.0,2500)
        rangeTup = ( ecRange, compRange, shutterRange, intensity397Range )
        for dev, value in zip( devTup, rangeTup ): d[dev]['range'] = value
        self.dcDict = d

    @inlineCallbacks
    def checkQueue( self ):
        """
        When timer expires, check for voltage to write
        """
        if self.queue:
            print 'clearing queue...(%d items)' % len( self.queue )
            yield self.writeToSerial( *self.queue.pop( 0 ) )
        else:
            print 'queue free for writing'
            self.free = True

    def tryToSend( self, channel, value ):
        if self.free:
            self.free = False
            self.writeToSerial( channel, value )
        elif len( self.queue ) > MAX_QUEUE_SIZE:
            raise DCBoxError( 2 )
        else: self.queue.append( ( channel, value ) )

    def writeToSerial( self, channel, value ):
        """
        Forbids write requests for specific time waitTime.
        Writes command and saves it to memory
        """
        self.checkConnection()
        reactor.callLater( self.waitTime, self.checkQueue )
        toSend = self.mapMessage( channel, value )
        self.ser.write( toSend )
        dev, devChannel = self.getChannelInfo( channel )
        self.dcDict[dev]['devChannels'][devChannel]['value'] = value

    def validateDevChannel( self, dev, devChannel ):
        d = self.dcDict
        if devChannel not in d[dev]['devChannels'].keys(): raise DCBoxError( 0 )

    def validateInput( self, dev, value ):
        d = self.dcDict
        if dev == 'shutter' and not isinstance( value, bool ): raise DCBoxError( 3 )
        else:
            MIN, MAX = d[dev]['range']
            if not MIN <= value <= MAX: raise DCBoxError( 1 )


    @setting( 0 , devChannel = 'w: which end cap (1 or 2)',
              voltage = 'v: voltage to apply',
              returns = '' )
    def setEndCap( self, c, devChannel, voltage ):
        """
        Sets endcap voltage
        """
        dev = 'endcap'
        self.validateDevChannel( dev, devChannel )
        self.validateInput( dev, voltage )
        channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
        self.tryToSend( channel, voltage )

    @setting( 1 , devChannel = 'w: which end cap(1 or 2)',
              returns = 'v: voltage' )
    def getEndCap( self, c, devChannel ):
        dev = 'endcap'
        self.validateDevChannel( dev, devChannel )
        return self.dcDict[dev]['devChannels'][devChannel]['value']

    @setting( 2, devChannel = ['w: which electrode (1 or 2)',
                               's: which electrode ("common")'],
              voltage = 'v: voltage to apply',
              returns = '' )
    def setComp( self, c, devChannel, voltage ):
        """
        Sets compensation electrode voltages
        """
        dev = 'comp'
        self.validateDevChannel( dev, devChannel )
        self.validateInput( dev, voltage )
        channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
        self.tryToSend( channel, voltage )

    @setting( 3 , devChannel = ['w: which electrode (1 or 2)',
                                's: which electrode ("common")'],
              returns = 'v: voltage' )
    def getComp( self, c, devChannel ):
        dev = 'comp'
        self.validateDevChannel( dev, devChannel )
        return self.dcDict[dev]['devChannels'][devChannel]['value']

    @setting( 4, devChannel = 'w: which shutter (1-3)',
             state = 'b: open (true) or shut (false)',
             returns = '' )
    def setShutter( self, c, devChannel, state ):
        """
        Sets compensation electrode voltages
        """
        dev = 'shutter'
        self.validateDevChannel( dev, devChannel )
        self.validateInput( dev, state )
        channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
        self.tryToSend( channel, state )

    @setting( 5 , devChannel = 'w: which shutter (1-3)',
              returns = 'b: open (true) or shut (false)' )
    def getShutter( self, c, devChannel ):
        dev = 'shutter'
        self.validateDevChannel( dev, devChannel )
        return self.dcDict[dev]['devChannels'][devChannel]['value']
    
    @setting( 6, voltage = 'v: voltage to apply',
             returns = '' )
    def setIntensity397( self, c, voltage):
        """
        Sets level for intensity stabilization
        """
        dev = devChannel = '397intensity'
        self.validateDevChannel( dev, devChannel )
        self.validateInput( dev, voltage )
        channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
        self.tryToSend( channel, voltage )
    
    @setting(7,returns ='v: voltage')
    def getIntensity397(self):
       dev = devChannel = '397intensity'
       self.validateDevChannel( dev, devChannel )
       return self.dcDict[dev]['devChannels'][devChannel]['value']
    
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
        def mapVoltage( value, range ):
            return ( float( value ) - float( range[0] ) ) * DAC_MAX / ( range[1] - range[0] )
        d = self.dcDict
        dev = self.getChannelInfo( channel )[0]
        range = d[dev]['range']
        if dev == 'shutter': value = range[1] if value else range[0]
        return self.makeComString( channel, self.voltageToFormat( mapVoltage( value, range ) ) )

    def getChannelInfo( self, channel ):
        d = self.dcDict
        for dev in d:
            for devChannel in d[dev]['devChannels']:
                if d[dev]['devChannels'][devChannel]['channel'] == channel: return ( dev, devChannel )

if __name__ == "__main__":
    from labrad import util
    util.runServer( DCBoxServer() )


