"""
### BEGIN NODE INFO
[info]
name = AC Server
version = 2.0
description = 
instancename = AC Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks#, returnValue, DeferredLock
import numpy
#store PID, integrator in the registry
class AlarmChecker():

    timeToReset = 6*3600  # set time for next alarm to 6 hours
    messageMax = 1 #maximum number of allowed emails per the number of callstoReset
    
    def __init__(self, emailer):
        self.emailer = emailer
        self.messageSent = 0
    
    def check(self, temperature):
        pass

class RunningAverage():
    """Allows for smoothing of input data by taking a running average"""
    def __init__(self, arrLength, averageNumber):
        self.historyArray = numpy.zeros((averageNumber,arrLength))
        self.averageNumber = averageNumber
        self.counter = 0
        self.filled = False
    
    def add(self, addition):
        self.historyArray[self.counter] = addition 
        self.counter = (self.counter + 1) % averageNumber
        if self.counter == 0: self.filled = True
    
    def getAverage(self):
        if self.filled:
            average = numpy.average(self.historyArray, 0)
        else:
            average = numpy.sum(self.historyArray, 0) / self.counter
        return average      
class PIDcontroller:
    pass

class AC_Server( LabradServer ):
    name = 'AC Server'
    
    @inlineCallbacks
    def initServer( self ):
        self.manualOverwrite = False
        self.manualPositions = None####
        self.PIDparams =[0,0,0]####get from registry
        yield None

    @setting(0, 'Manual Override', enable = 'b', valvePositions = '*v')
    def manualOverride(self, enable, valvePositions = None):
        """If enabled, allows to manual specify the positions of the valves, ignoring feedback"""
        self.manualOverwrite = enable
        pass
    
    @setting(1, 'PID Parameters', PID = '*3v')
    def PID(self, PID = None):
        """Allows to view or to set the PID parameters"""
        if PID is None: return self.PID
        self.PIDparams = PID
    
    @setting(2, 'Reset Integrator')
    def resetIntegrator(self):
        pass
       
    


#class ADC():
#    V0 = 6.95 #volts on the voltage reference
#    hardwareGain = [15,15,15,15,15,15,15,15,15,15,15,15,5,15,5,15] #channels 13 and 15 (or 12,14 counting from 0) have less gain for expanded range
#    
#    def voltToRes(self):
#
#    def binarytoTempC(self,bin, ch): #converts binary output to a physical temperature in C
#        Vin = 2.56*(float(bin)+1)/1024 #voltage that is read in 1023 is 2.56 0 is 0
#        
#        dV = (15/HardwareG[ch])*(Vin/1.2 - 1) #when G = 15 (most channels) dV of 2.4 corresponds to bridge voltage of 1 and dV of 0 is bridge voltage of -1     
#                    #G = 5 for low res channels for cold water, hot water supply
#                    #G is determines by INA114 gain resistor
#        R = (dV/V0 +.5) / (- dV/V0 + .5) * 10 #convert bridge voltage to R in kohms
#        T = 1/(a + b*math.log(R/10.) + c * pow(math.log(R/10.),2) + d * pow(math.log(R/10.),3)) #consult datasheet for this
#        TempC = round(T - 273.15,2) #Kelvin to C
#        return TempC


class thermistor():
    #defining coefficients for voltage to temperature conversion, taken info from thermistor datasheet
    a = 3.3540154e-03 
    b = 2.5627725e-04 
    c = 2.0829210e-06
    d = 7.3003206e-08
    V0 = 6.95 #volts on the voltage reference
    
    def resToTemp(self, R):
        '''takes the resistance R in Kohms and converts this to temperature in Celcius'''
        T = 1/(self.a + self.b*numpy.log(R/10.) + self.c * pow(numpy.log(R/10.),2) + self.d * pow(numpy.log(R/10.),3)) #datasheet
        TempC = round(T - 273.15,2) #Kelvin to C
        return TempC


if __name__ == "__main__":
    from labrad import util
    util.runServer(AC_Server())
