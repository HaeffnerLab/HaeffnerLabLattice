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
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
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
        self.counter = (self.counter + 1) % self.averageNumber
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
    updateRate = 1.0 #seconds
        
    @inlineCallbacks
    def initServer( self ):
        self.daq = DataAcquisition()
        self.channels = self.daq.channels
        self.averager = RunningAverage(self.channels, averageNumber = 12)
        self.manualOverwrite = False
        self.manualPositions = None####
        self.PIDparams =[0,0,0]####get from registry
        self.inControl = LoopingCall(self.control)
        self.inControl.start(self.updateRate)
        self.daqErrors = 0
        yield None

    @setting(0, 'Manual Override', enable = 'b', valvePositions = '*v')
    def manualOverride(self, c, enable, valvePositions = None):
        """If enabled, allows to manual specify the positions of the valves, ignoring feedback"""
        self.manualOverwrite = enable
        pass
    
    @setting(1, 'PID Parameters', PID = '*3v')
    def PID(self, c, PID = None):
        """Allows to view or to set the PID parameters"""
        if PID is None: return self.PID
        self.PIDparams = PID

    @setting(2, 'Reset Integrator')
    def resetIntegrator(self, c):
        pass
    
    @inlineCallbacks
    def control(self):
        try:
            temps = yield self.daq.getTemperatures()
        except: #put error type
            self.daqErros += 1
            yield self.checkMaxErrors()
        else:
            self.averager.add(temps)
            temps = self.averager.getAverage()
            
    
    @inlineCallbacks
    def checkMaxErrors(self):
        """checks how many errors have occured in sends out a notification email"""
        if self.daqErrors >  self.maxDaqErrors:
            print "TOO MANY DAQ ERRORS"
            #yield self.emailer.send()...
            self.daqErrors = 0
    
class DataAcquisition():
    channels = 16
    hardwareGain = numpy.array([15,15,15,15,15,15,15,15,15,15,15,15,5,15,5,15]) #channels 13 and 15 (or 12,14 counting from 0) have less gain for expanded range
    V0 = 6.95 #volts on the voltage reference
    
    def __init__(self, serial):
        self.serial = serial
        self.thermistor = thermistor()
    
    @inlineCallbacks
    def getTemperatures(self):
        binary = yield self.readADC()
        temperatures = self.binarytoTemp(binary)
        returnValue(temperatures)
    
    def binarytoTempC(self,binary):
        '''converts binary output to a physical temperature in C'''
        Vin = 2.56*(binary + 1.)/1024. #voltage that is read in 1023 is 2.56 0 is 0
        dV = (15./self.hardwareGain)*(Vin/1.2 - 1) #when G = 15 (most channels) dV of 2.4 corresponds to bridge voltage of 1 and dV of 0 is bridge voltage of -1     
                    #G = 5 for low res channels for cold water, hot water supply
                    #G is determines by INA114 gain resistor
        R = (dV/self.V0 +.5) / (- dV/self.V0 + .5) * 10 #convert bridge voltage to R in kohms
        TempC = self.thermistor.resToTemp(R)
        return TempC
    
    @inlineCallbacks
    def readADC(self):
        '''Processing the input in the format 03:1023<space>... where 03 is the number of the detector, 1023 is the voltage representation''' 
        yield self.serial.write('t') #command to output readings
        reading = yield self.serial.read(self.channels*8) #reads 128 bytes, 16 channels 7 bytes each and 16 spaces
        reading = reading.split(' ')
        for index,element in enumerate(reading):
            reading[index] = float(element.partition(':')[2])
        reading = numpy.array(reading)
        return reading

class thermistor():
    #defining coefficients for voltage to temperature conversion, taken info from thermistor datasheet
    a = 3.3540154e-03 
    b = 2.5627725e-04 
    c = 2.0829210e-06
    d = 7.3003206e-08
    
    def resToTemp(self, R):
        '''takes the resistance R in Kohms and converts this to temperature in Celcius'''
        T = 1./(self.a + self.b*numpy.log(R/10.) + self.c * pow(numpy.log(R/10.),2) + self.d * pow(numpy.log(R/10.),3)) #datasheet
        TempC = round(T - 273.15,2) #Kelvin to C
        return TempC


if __name__ == "__main__":
    from labrad import util
    util.runServer(AC_Server())
