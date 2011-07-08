# -*- coding: utf-8 -*-
'''
Created on Dec 22, 2010

@author: christopherreilly, Michael Ramm

Remotely controls DC voltage supply
'''

from serialdeviceserver import SerialDeviceServer, SerialDeviceError, setting, inlineCallbacks, SerialConnectionError, Error
from string import replace
from twisted.internet import reactor
import binascii

NAME = 'LaserDAC'
REGPORTNAME = 'LaserRoomDac'
SERIALSERVERNAME = 'lattice_pc_serial_server'

prec_bits = 16.
dac_max = 2500. #mV

class DCVSError( Exception ):
    pass

class LaserDac( SerialDeviceServer ):
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
            self.port = yield self.getPortFromReg(REGPORTNAME)
            port = self.port
            serStr = SERIALSERVERNAME
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
                yield self.writeToSerial( toWrite[0],toWrite[1] )
                self.toWrite = None
            except Error:
                raise
        else:
            print 'queue free for writing'
            self.free = True

    @inlineCallbacks
    def writeToSerial( self, ch, toSer ):
        """
        Forbids write requests for specific time waitTime.
        Writes command and saves it to memory
        """
        self.free = False
        yield reactor.callLater( self.waitTime, self.checkQueue )
        yield self.ser.write( self.MakeComString(ch, self.VoltageToFormat( toSer ) ) )
        self.lastVoltage = toSer

    @setting( 0, 'Write Voltage', channel = "w", voltage = "v" , returns="")
    def writeVoltage( self, c, channel, voltage ):
        """
        Changes the DC voltage supply (for end cap).
        Enter a floating point value in volts
        """
        if self.free:
            try:
                yield self.writeToSerial(channel, voltage )
            except SerialConnectionError, e:
                print str( e )
                print 'Error: disconnecting...'
                self.disconnect()
        else:
            self.toWrite = [channel,voltage]
            
    @setting( 1, 'Get Voltage', returns = 'v: previous voltage' )
    def getVoltage( self, c ):
        return self.lastVoltage
        
#DAC is 16 bit, so the function accepts voltage in mv and converts it to a sequential representation
#2500 -> 2^16 , #1250 -> 2^15
    def VoltageToFormat( self, voltage ):
        return int((2.**prec_bits - 1)  * voltage / dac_max )

#converts sequential representation to string understood by microcontroller
#i.e ch 1 set 2500mv -> '1,str' where str =  is  character representation of 0xffff given by binascii.unhexlify(ffff)
    def MakeComString(self,ch,seq):
	hexrepr = hex(seq)[2:] #select ffff out of 0xfff'
	hexrepr = hexrepr.zfill(4) #left pads to make sure 4 characters 
	numstr = binascii.unhexlify(hexrepr) #converts ffff to ascii characters
	comstring = str(ch) + ',' + numstr
	return comstring

if __name__ == "__main__":
    from labrad import util
    util.runServer(LaserDac())
