#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO:
# 1. Error handling for failed connections
# 2. Separate function for boundchecking of the set voltages

from labrad.server import LabradServer, setting
import serial 

portA = 'COM6'
portB = 'COM5'
#serA = serial.Serial(portA)
#serB = serial.Serial(portB)

class DCServer(LabradServer):
    """Sets DC Voltages"""
    name = "%LABRADNODE% DC Server"
    
    def initContext( self , c ):
	    c['dict'] = {}

    @setting(1, "Set", voltage_A = "v", voltage_B = "v" , returns="")
    def Set( self , c , voltage_A , voltage_B ):
	    """Set voltages"""
	    c['dict']['voltage_A'] = voltage_A
	    c['dict']['voltage_B'] = voltage_B
	    toSerialA = MakeComString( VoltagetoFormat(voltage_A) )
	    toSerialB = MakeComString( VoltagetoFormat(voltage_B) )
#	    serA.write(toSerialA)	    
#	    serB.write(toSerialB)

    @setting(2, "Get", returns="*v")
    def Get( self , c ):
	    return [c['dict']['voltage_A'], c['dict']['voltage_B']]


#function converts input voltage to microcontroller scale
#1023 is 4000 volts, scale is linear
def VoltagetoFormat(volt):
	if (volt < 0 or volt > 4000):
		volt = 0
		print 'wrong voltage entered'
		num = round((volt/4000.0)*1023)
		return int(num)
		    
#takes a a number of converts it to a string understood by microcontroller, i.e 23 -> C0023!
def MakeComString(num):
	comstring = 'C' + str(num).zfill(4) + '!'
	return comstring

if __name__ == "__main__":
	from labrad import util
	util.runServer(DCServer())