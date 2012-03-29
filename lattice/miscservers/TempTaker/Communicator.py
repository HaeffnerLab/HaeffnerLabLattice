import numpy
from twisted.internet.defer import inlineCallbacks, returnValue

class Communicator():
    channels = 16
    hardwareGain = numpy.array([15,15,15,15,15,15,15,15,15,15,15,15,5,15,5,15]) #channels 13 and 15 (or 12,14 counting from 0) have less gain for expanded range
    V0 = 6.95 #volts on the voltage reference
    #dictionary of locations and corresponding array elements i.e table3 corresponds to hardwareGain[0]
    channelDict = {'Table1':7, #### Big Table Big Room
                   'Table3':0, #### small room
                   'Table4':5, #### laser room
                   'SupplyBigRoom':13,
                   'SupplyLaserRoom':15,
                   'SupplySmallRoom':10,
                   'ColdWater':14,
                   'HotWater':12
                   }
    
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
    
    @inlineCallbacks
    def setValves(self, signal):
        for i in range(signal):
            yield self.serial.write("d")
            yield self.serial.write(str(i))
            vsig = self.dec2hex(signal[i])
            yield self.serial.write(vsig)

    def dec2hex(self, n):#"""return the hexadecimal string representation of integer n as a two digits representation in lowercase"""
        n = int(n)
        string = "%x" % n
        string = string.zfill(2)
        return string


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