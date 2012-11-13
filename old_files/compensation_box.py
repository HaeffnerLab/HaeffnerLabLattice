from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
import binascii

SERVERNAME = 'Compensation Box'
PREC_BITS = 16.
DAC_MAX = 2500.
MAX_QUEUE_SIZE = 1000
TIMEOUT = 1.0 #time to wait for response from dc box
RESP_STRING = 'r' #expected response from dc box after write
ERROR_TIME = 1.0 #time to wait if correct response not received

class DCBoxError( SerialConnectionError ):
    errorDict = {
        0:'Invalid device channel',
        1:'Value out of range',
        2:'Queue size exceeded',
        4:'Must set value before you can retrieve',
        5:'Correct response from DC box not received, sleeping for short period'
        }

class CompensationBox( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'COMPBOX'
    port = None
    serNode = 'lattice-pc'
    timeout = TIMEOUT

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
        self.performCalibration()
        self.setupLineScan()
        yield self.populateDict()
        self.currentContexts = []
        self.free = True

    def createDict( self ):
        """
        Initializes dictionary object (dcDict)
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
        devTup = ( 'compensation',)
        for dev in devTup:
            d[dev] = {'devChannels':{}}
        #chanTup =  ( ( ( 1, 0, ( 0, 2**16 - 1) ), ( 2, 1, ( 0 , 2**16-1) ) ) ,) #useful for calibration
        chanTup =  ( ( ( 1, 0, ( -479, -10) ), ( 2, 1, ( -479, -10) ) ) ,) #range refers to device range available for setting
        for dev, value in zip( devTup, chanTup):
            for chanPair in value:
                    d[dev]['devChannels'][chanPair[0]] = {'value':None, 'channel':chanPair[1] ,'range': chanPair[2]}
        self.dcDict = d
        
    def performCalibration(self):
        #calibration with two points in the format (voltage, sequential DAC)
        calibration = ((1,((-7.67, 2000), (-479.9, 2**16 - 1))), (2,((-7.82, 2000), (-483.3, 2**16 - 1))) )
        for chan, points in calibration:
            m = ( points[1][1] - points[0][1] ) / ( points[1][0] - points [0][0] )
            b = points[0][1] - m * points[0][0]
            self.dcDict['compensation']['devChannels'][chan]['calib slope'] = m
            self.dcDict['compensation']['devChannels'][chan]['calib intercept'] = b
    
    def setupLineScan(self):
        #ability to do line scans i.e scan c1 and have c2 = slope * c1 + offset
        self.dcDict['compensation']['linescan slope'] = 1.89
        self.dcDict['compensation']['linescan offset'] = None
        self.dcDict['compensation']['linescan parameter'] = None
        
    def updateLineScanValues(self):
        m = self.dcDict['compensation']['linescan slope']
        c1 = self.dcDict['compensation']['devChannels'][1]['value']
        c2 = self.dcDict['compensation']['devChannels'][2]['value']
        self.dcDict['compensation']['linescan offset'] = c2 - m * c1
        self.dcDict['compensation']['linescan parameter'] = c1
    
    def updateCompensationfromLineScan(self):
        m = self.dcDict['compensation']['linescan slope']
        parameter = self.dcDict['compensation']['linescan parameter']
        offset = self.dcDict['compensation']['linescan offset']
        c1 = parameter
        c2 = m * c1 + offset
        self.dcDict['compensation']['devChannels'][1]['value'] = c1
        self.dcDict['compensation']['devChannels'][2]['value'] = c2
               
    @inlineCallbacks
    def populateDict(self):
        """
        Gets the information about the current setting from the hardware
        """
        for dev in self.dcDict:
            for devChannel in self.dcDict[dev]['devChannels']:
                channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
                range = self.dcDict[dev]['devChannels'][devChannel]['range']
                print channel
                comstring = str(channel)+'r'
                yield self.ser.write(comstring)
                encoded = yield self.ser.read(3)
                seq = int(binascii.hexlify(encoded[0:2]),16)
                print seq
                voltage = self.seqToVoltage(devChannel, seq)
                print voltage
                self.dcDict[dev]['devChannels'][devChannel]['value'] = voltage
        self.updateLineScanValues()
                
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
#            Since we didn't get the the correct response,
#            place the value back in the front of the queue
#            and wait for a specified ERROR_TIME before
#            checking the queue again.
            self.queue.insert( 0, ( channel, value ) )
            reactor.callLater( ERROR_TIME, self.checkQueue )
            raise DCBoxError(5)
        else:
#            Since we got the correct response,
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

    def validateInput( self, dev, devchannel, value ):
        """
        Check to see if value lies within specified device's range.
        
        @param dev: DC Box device
        @param value: DC Box device value
        
        @raise DCBoxError: Error code 3.  Value not within device's range.
        """
        d = self.dcDict
        MIN, MAX = d[dev]['devChannels'][devchannel]['range']
        if not MIN <= value <= MAX: raise DCBoxError( 1 )


    @setting( 0, devChannel = 'w: which electrode (1 or 2)', voltage = 'v: voltage to apply', returns = '' )
    def setComp( self, c, devChannel, voltage ):
        """
        Sets compensation electrode voltages.
        """
        dev = 'compensation'
        self.validateDevChannel( dev, devChannel )
        self.validateInput( dev, devChannel, voltage )
        channel = self.dcDict[dev]['devChannels'][devChannel]['channel']
        self.tryToSend( channel, voltage )
        self.updateLineScanValues()
        self.currentContexts = [c.ID]

    @setting( 1 , devChannel = 'w: which electrode (1 or 2)', returns = 'v: voltage' )
    def getComp( self, c, devChannel ):
        """
        Retrieve compensation voltage for specified device channel.
        """
        dev = 'compensation'
        self.validateDevChannel( dev, devChannel )
        value = self.dcDict[dev]['devChannels'][devChannel]['value']
        if value is not None: return value
        else: raise DCBoxError( 4 )
    
    @setting(2,  devChannel = 'w: which electrode (1 or 2)', returns = '*v: range' )
    def getRange(self, c, devChannel):
        """
        Returns range of the specified device channel
        """
        dev = 'compensation'
        self.validateDevChannel( dev, devChannel )
        range = self.dcDict[dev]['devChannels'][devChannel]['range']
        if range is not None: return range
        else: raise DCBoxError( 4 )
    
    @setting(3, returns = 'b')
    def updatedDifferentContext(self, c):
        """
        returns if current context was the last one to update the server
        """
        if c.ID not in self.currentContexts:
            self.currentContexts.append(c.ID)
            ans = True
        else:
            ans = False
        return ans
    
    @setting(4, slope = 'v: set slope for line scan', returns = '')
    def setLineScanSlope(self, c, slope):
        self.dcDict['compensation']['linescan slope'] = slope
        
    @setting(5, offset = 'v: offset for line scan', returns = '')
    def setLineScanOffset(self, c, offset):
        dev = 'compensation'
        self.dcDict[dev]['linescan offset'] = offset
        self.updateCompensationfromLineScan()
        for i in [1,2]:
            voltage = self.dcDict[dev]['devChannels'][i]['value']
            self.validateInput( dev, i, voltage )
            channel = self.dcDict[dev]['devChannels'][i]['channel']
            self.tryToSend( channel, voltage )  
        self.currentContexts = [c.ID]      
    
    @setting(6, returns = '*v')
    def getLineScanValues(self, c):
        slope = self.dcDict['compensation']['linescan slope']
        offset = self.dcDict['compensation']['linescan offset']
        parameter = self.dcDict['compensation']['linescan parameter']
        return [slope, offset, parameter]
        
    @setting(7, parameter = 'v: parameter c1 to move along the line scan', returns = '')
    def setLineScanValue(self, c, parameter):
        dev = 'compensation'
        self.dcDict[dev]['linescan parameter'] = parameter
        self.updateCompensationfromLineScan()
        for i in [1,2]:
            voltage = self.dcDict[dev]['devChannels'][i]['value']
            self.validateInput( dev, i, voltage )
            channel = self.dcDict[dev]['devChannels'][i]['channel']
            self.tryToSend( channel, voltage )  
        self.currentContexts = [c.ID]      
    #converts sequential representation to string understood by microcontroller                                                                                                        
    #i.e ch 1 set to maximum, which is sequentially 2**16-1 or ffff in hex -> '1,str' where str =  is character representation of 0xffff given by binascii.unhexlify(ffff)
    @staticmethod
    def makeComString( channel, binVolt ):
        hexrepr = hex( binVolt )[2:] #select ffff out of 0xfff'                                                                                                                          
        hexrepr = hexrepr.zfill( 4 ) #left pads to make sure 4 characters                                                                                                            
        numstr = binascii.unhexlify( hexrepr ) #converts ffff to ascii characters                                                                                                    
        comstring = str( channel ) + ',' + numstr
        return comstring

    def seqToVoltage(self, channel, seq):
        m = self.dcDict['compensation']['devChannels'][channel]['calib slope']
        b = self.dcDict['compensation']['devChannels'][channel]['calib intercept']
        voltage = (seq  - b) / m
        return voltage
    
    def volToSequential(self, channel, voltage):
        m = self.dcDict['compensation']['devChannels'][channel]['calib slope']
        b = self.dcDict['compensation']['devChannels'][channel]['calib intercept']
        seq = int(round( m * voltage + b ))
        return seq
    
    def mapMessage( self, channel, value ):
        d = self.dcDict
        dev, devChannel = self.getChannelInfo( channel )
        return self.makeComString( channel, self.volToSequential( devChannel, value ) )

    def getChannelInfo( self, channel ):
        d = self.dcDict
        for dev in d:
            for devChannel in d[dev]['devChannels']:
                if d[dev]['devChannels'][devChannel]['channel'] == channel: return ( dev, devChannel )

if __name__ == "__main__":
    from labrad import util
    util.runServer( CompensationBox() )