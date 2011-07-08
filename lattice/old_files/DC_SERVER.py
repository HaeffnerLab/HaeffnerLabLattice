
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

from labrad.server import LabradServer, setting
import serial 
from threading import Timer

class DCServer(LabradServer):
    """Sets DC Voltages"""
    name = "%LABRADNODE% DC Server"
    
    def initServer( self ):
        
        #the current voltages
        self._voltages = []

        #voltages to write while writing is blocked
        self._vToWrite = []

        #port names
        self._ports = [ 'COM6' , 'COM5' ] #format is ['portA','portB']

        #serial connections for ports(commented out for debugging purposes)
        self._ser = [ serial.Serial(x) for x in self._ports ]

        #time between serial writes ( in seconds )
        self._waitTime = 0.100

        #boolean indicating whether the server is accepting writes
        self._free = True

    #Disables serial port for further writes, then writes
    def writeVoltages( self, v ):
        self._free = False
        Timer( self._waitTime , self.checkForUpdates ).start()
        self._voltages = v
        #Bug in the list comprehension below
        v = [ MakeComString( VoltageToFormat( x ) ) for x in v ]
        for i in range( len(v) ):
            print v[i]
            self._ser[i].write(v[i])

    #Called when timer expires
    def checkForUpdates( self ): 
        if self._vToWrite:
            self.writeVoltages( self._vToWrite )
            self._vToWrite = []
        else:
            self._free = True

    @setting(1, "Set", voltage_A = "v", voltage_B = "v" , returns="")
    def Set( self , c , voltage_A , voltage_B ):
        """Set voltages"""
        voltages = [ voltage_A , voltage_B ]
        if self._free:
            if voltages != self._voltages:
                self.writeVoltages( voltages )
        else:
            if voltages != self._vToWrite:
                self._vToWrite = voltages

    @setting(2, "Get", returns="*v")
    def Get( self , c ):
        """Get voltages"""
        return self._voltages

#function converts input voltage to microcontroller scale
#1023 is 4000 volts, scale is linear
def VoltageToFormat(volt):
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
