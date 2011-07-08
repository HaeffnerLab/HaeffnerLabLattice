# DC VOLTAGE SUPPLY CONTROL
# DOES NOT MAKE CALLS TO
# OTHER LABRAD SERVERS
# 2010 - 12 - 14: Updated to accept voltages in float form
# 2010 - 12 - 14: Removed 'Server' from server name for obvious reasons

from serialdeviceserver import SerialDeviceServer, SerialDeviceError, setting
from threading import Timer
from string import replace

NAME = 'DC0'

class DCVSError( SerialDeviceError ):
    pass

class DC0Server( SerialDeviceServer ):
    """Controls DC voltages supply"""
    name = NAME
    waitTime = .1
    
    # To write to a specific port (instead of using standard input),
    # get rid of the 'initServer' call.
    # Replace it with a call to another superclass method 'initSerial',
    # specificying the port as a function parameter (e.g. port = 'COM5')
    # Feel free to also hard-code in a waitTime instead of receiving it
    # from standard input.
    def initServer(self):
        """
        Remember to call the super class initServer method,
        that initializes the serial connection represented by
        class member 'ser'.
        Otherwise we set up DCVS specific things here.
        """
        self.initSerial( port = 'COM5' )
        while not self.waitTime:
            print 'Set min time between writes:'
            self.waitTime = raw_input()
            #validate input
            if not replace( self.waitTime , '.' , '' , 1 ).isdigit():
                self.waitTime = None
            else:
                self.waitTime = float(self.waitTime)
        self.toWrite = None
        self.lastVoltage = None
        self.free = True
                
    def checkQueue(self):
        """
        When timer expires, check for voltage to write
        """
        if self.toWrite:
            try:
                self.writeToSerial(self.toWrite)
                self.toWrite = None
            except:
                raise SerialDeviceError( 'Problem with serial connection' )
        else:
            self.free = True
    
    def writeToSerial( self, toSer ):
        """
        Forbids write requests for specific time waitTime.
        Writes command and saves it to memory
        """        
        self.free = False
        Timer( self.waitTime , self.checkQueue ).start()
        self.ser.write( self.MakeComString( self.VoltageToFormat(toSer) ) )
        self.lastVoltage = toSer

    @setting(0, 'Write Voltage', volt = 'v: Voltage to write', returns=[''])
    def writeVoltage(self, c, volt):
        """
        Changes the DC voltage supply (for end cap).
        Enter a floating point value in volts
        """
        if self.free:
            self.writeToSerial( toSer = volt )
        else:
            self.toWrite = volt

    @setting(1, 'Get Voltage', returns='v: previous voltage')
    def getVoltage(self, c):
        return self.lastVoltage
    
    def VoltagetoFormat(volt):
        """
        function converts input voltage to microcontroller scale
        1023 is 4000 volts, scale is linear
        """
        if not  0 < volt < 4000: raise DCVSError( 'voltage not in range' )
        num = round((volt/4000.0)*1023)
        return int(num)

    def MakeComString(num):
        """
        takes a a number of converts it to a string understood by microcontroller, i.e 23 -> C0023!
        """
        comstring = 'C' + str(num).zfill(4) + '!'
        return comstring
       
if __name__ == "__main__":
    from labrad import util
    util.runServer(DC0Server())
