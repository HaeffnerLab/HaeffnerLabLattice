'''
Created on Dec 22, 2010

@author: christopherreilly

Remotely controls DC voltage supply
'''


from serialdeviceserver import SerialDeviceServer, SerialDeviceError, setting, inlineCallbacks, SerialConnectionError, Error
from string import replace
from twisted.internet import reactor

NAME = 'DC0'

class DCVSError( Exception ):
    pass

class DC0Server( SerialDeviceServer ):
    """Controls DC voltages supply"""
    name = NAME
    waitTime = 2

    # To write to a specific port (instead of using standard input),
    # get rid of the 'initServer' call.
    # Replace it with a call to another superclass method 'initSerial',
    # specificying the port as a function parameter (e.g. port = 'COM5')
    # Feel free to also hard-code in a waitTime instead of receiving it
    # from standard input.
    @inlineCallbacks
    def initServer( self ):
        try:
            self.port = yield self.selectPortFromReg()
            port = self.port
            serStr = yield self.findSerial()
            self.initSerial( serStr = serStr , port = port )
        except SerialConnectionError, e:
            if e.code == 0:
                print str( e )
                print 'Please start up the serial server'
            else: raise
        while not self.waitTime:
            print 'Set min time between writes:'
            self.waitTime = raw_input()
            #validate input
            if not replace( self.waitTime , '.' , '' , 1 ).isdigit():
                self.waitTime = None
            else:
                self.waitTime = float( self.waitTime )
        self.toWrite = None
        self.lastVoltage = None
        self.free = True

    def setFree( self ):
        self.free = True

    @inlineCallbacks
    def checkQueue( self ):
        """
        When timer expires, check for voltage to write
        """
        if self.toWrite:
            try:
                print 'clearing queue...'
                toWrite = self.toWrite
                yield self.writeToSerial( toWrite )
                self.toWrite = None
            except Error:
                raise
        else:
            print 'queue free for writing'
            self.free = True

    @inlineCallbacks
    def writeToSerial( self, toSer ):
        """
        Forbids write requests for specific time waitTime.
        Writes command and saves it to memory
        """
        self.free = False
        yield reactor.callLater( self.waitTime, self.checkQueue )
        yield self.ser.write( self.MakeComString( self.VoltageToFormat( toSer ) ) )
        self.lastVoltage = toSer

    @setting( 0, 'Write Voltage', volt = 'v: Voltage to write', returns = [''] )
    def writeVoltage( self, c, volt ):
        """
        Changes the DC voltage supply (for end cap).
        Enter a floating point value in volts
        """
        if self.free:
            try:
                yield self.writeToSerial( volt )
            except SerialConnectionError, e:
                print str( e )
                print 'Error: disconnecting...'
                self.disconnect()
        else:
            self.toWrite = volt

    @setting( 1, 'Get Voltage', returns = 'v: previous voltage' )
    def getVoltage( self, c ):
        return self.lastVoltage

    def VoltageToFormat( self, volt ):
        """
        function converts input voltage to microcontroller scale
        1023 is 4000 volts, scale is linear
        """
        if not  0 < volt < 4000: raise DCVSError( 'voltage not in range' )
        num = round( ( volt / 4000.0 ) * 1023 )
        return int( num )

    def MakeComString( self, num ):
        """
        takes a a number of converts it to a string understood by microcontroller, i.e 23 -> C0023!
        """
        comstring = 'C' + str( num ).zfill( 4 ) + '!'
        return comstring


if __name__ == "__main__":
    from labrad import util
    util.runServer( DC0Server() )
