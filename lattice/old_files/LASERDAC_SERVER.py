# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO: While we are only writing software to
# control ONE pair of DC Voltages, it doesn't
# seem reasonable to assign clients their own
# set of voltages (like in the last version).
# Instead, we should only have one set of
# voltages regardless of context (i.e. client)
# and later let the server control multiple
# pairs of DC voltage sources (if that is even
# useful). For now the server will only store
# one pair of voltages regardless of how many
# clients are connected.

#TODO1 central storage for settings, port names, last voltage sent?
#TODO2 debug mode that prevents that prints to screen instead of sending
#TODO3 implement with Labrad serial server
#TODO4 should allow to write voltages to multiple channels while keeping the 'waiting framework' or maybe
#this will be resolve with the twisted framework

from labrad.server import LabradServer, setting
import serial 
import binascii

prec_bits = 16.
dac_max = 2500. #mV

class DCServer(LabradServer):
    """Sets Voltages on Laser Room DAC"""
    name = "%LABRADNODE% Laser DAC Server"
    
    def initServer( self ):    
        #port names
        self._port = 'COM12'

        #serial connections for ports(commented out for debugging purposes)
        self._ser = serial.Serial(self._port)

    @setting(1, "Set", channel = "w", voltage = "v" , returns="")
    def Set( self , c , channel , voltage ):
        """Set voltages"""
        voltage = VoltageToFormat(voltage)
	command = MakeComString(channel, voltage)
	self._ser.write(command)
	

#DAC is 16 bit, so the function accepts voltage in mv and converts it to a sequential representation
#2500 -> 2^16 , #1250 -> 2^15
def VoltageToFormat(voltage):
    return int((2.**prec_bits - 1)  * voltage / dac_max )
    
#converts sequential representation to string understood by microcontroller
#i.e ch 1 set 2500mv -> '1,str' where str =  is  character representation of 0xffff given by binascii.unhexlify(ffff)
def MakeComString(ch,seq):
    hexrepr = hex(seq)[2:] #select ffff out of 0xfff'
    hexrepr = hexrepr.zfill(4) #left pads to make sure 4 characters 
    numstr = binascii.unhexlify(hexrepr) #converts ffff to ascii characters
    comstring = str(ch) + ',' + numstr
    return comstring

if __name__ == "__main__":
    from labrad import util
    util.runServer(DCServer())





