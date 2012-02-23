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

    timeToReset = 2*3600  # set time for next alarm to 2 hours
    messageMax = 1 #maximum number of allowed emails per the number of callstoReset
    
    def __init__(self, emailer, dict):
        self.Table1 = dict['Table1']
        self.Table3 = dict['Table3']
        self.Table4 = dict['Table4']
        self.ColdWater = dict['ColdWater']
        self.HotWater = dict['HotWater']
        self.emailer = emailer
        self.messageSent = 0
        self.alarmReset = LoopingCall(self.reset)
        self.alarmReset.start(self.timeToReset, now = False)
        
    def reset(self):
        self.messageSent = 0
    
    @inlineCallbacks
    def check(self, temp):
        message = None
        if(abs(temp[self.Table1] - 22) > 2):
            message = ('AC ALARM','The differential between Table1 temperature and setpoint exceeds norm')
        if(abs(temp[self.Table3] - 22) > 2):
            message = ('AC ALARM','The differential between Table3 temperature and setpoint exceeds norm')
        if(abs(temp[self.Table4] - 22) > 2):
            message = ('AC ALARM','The differential between Table4 temperature and setpoint exceeds norm')
        #if(abs(temp[self.ColdWater] - 9) > 9):
            #message = ('AC ALARM','Cold Water temperature is too far from norm')
        if(abs(temp[self.HotWater] - 45) > 35):  # Hot water varies really a lot
            message = ('AC ALARM','The HotWaterBigRoom temperature is too far from norm')
        if message and (self.messageSent < self.messageMax): 
            yield self.emailer.send(*message)
            self.messageSent +=1

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
        #setting up necessary objects
        self.daq = DataAcquisition()
        self.channels = self.daq.channels
        self.channelDict = self.daq.channelDict
        self.averager = RunningAverage(self.channels, averageNumber = 12)
        self.emailer = self.client.emailer
        yield self.emailer.set_recipients(['micramm@gmail.com']) # set this later
        self.alarmChecker = AlarmChecker(self.emailer, self.channelDict)
        self.responseCalc = ResponseCalculator()
        #stting up constants
        self.manualOverwrite = False
        self.manualPositions = None####
        self.PIDparams =[0,0,0]####get from registry
        self.daqErrors = 0
        #begin control
        self.inControl = LoopingCall(self.control)
        self.inControl.start(self.updateRate)


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
        ###
        
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
            yield self.alarmChecker.check(temps)
            
    @inlineCallbacks
    def checkMaxErrors(self):
        """checks how many errors have occured in sends out a notification email"""
        if self.daqErrors >  self.maxDaqErrors:
            print "TOO MANY DAQ ERRORS"
            yield self.emailer.send('AC ALARM: TOO MANY DAQ ERRORS', '')
            self.daqErrors = 0
            self.inControl.stop()
    
class ResponseCalculator():
    
    IntegrationMin = -500*5; #limit on how small integration response can get, modified later with I-gain and thus more than the max control signal makes not much sense, the 20 comes from the estimated cooling power rescaling (SetPoint-2)
    IntegrationMax = 700*5; #limit on how big integration response can get, modified later with the I-gain, the 60 comes from the estimated heating power rescaling
    
    def __init__(self, channels, (P,I,D), setpoints, integrated = None):
        self.lastErrSigArr = numpy.zeros(channels)
        self.P = P
        self.I = I
        self.D = D
        self.setpoints = setpoints
    
    def updateGains(self, (P,I,D)):
        #constants for PID in the format [big room , small room , laser room]
        self.P = P
        self.I = I
        self.D = D
    
    def calculateResponse(self, temp):
        error = temp - setpoint
        
        self.integralerrorSigArr = self.calcintegrator(self.integralerrorSigArr, self.errorSigArr)
        self.saveIntegralError(self.integralerrorSigArr)
        self.PIDresponseArr = self.findPIDresponse(self.errorSigArr, self.integralerrorSigArr,self.lastErrSigArr) 
        self.lastErrSigArr= self.errorSigArr
        self.valvesignalArr = self.CalcValveSignal(self.PIDresponseArr, curTempArr)

    
    def getResponse(self):
        return [self.PIDresponseArr,self.valvesignalArr]
    
    
        
    def saveIntegralError(self,integError):
        #print integError
        self.INTEGFILE.seek(0) #moves position to the beginning of the file
        pickle.dump(integError, self.INTEGFILE)
        self.INTEGFILE.truncate() 

        
 
        
    def calcintegrator(self,oldArr, newArr):
        TotalArr = oldArr + newArr
        # Normalize maximum by the mean of the integration constants
        minim = IntegrationMin/(-sum(self.I)/len(self.I))
        maxim = IntegrationMax/(-sum(self.I)/len(self.I))
        TotalArr=clip(TotalArr,minim,maxim)
        return TotalArr
            
    def findPIDresponse(self,curErrArr, IntErrArr, lastErrArr):    #produces array containg signal to be sent to valves in format [Control1, Control2..] where each one is measured from -255 to 255 positive to hotter, negative for colder
        P = self.P
        I = self.I
        D = self.D
        propArr = zeros(ControlCh)
        propArr[bigroomctrl] = PSup[bigroomctrl]*curErrArr[SupplyBigRoom-1] + PTab[bigroomctrl]*curErrArr[Table1-1] + PCoolingWater[bigroomctrl]*curErrArr[ColdWaterBigRoom]
        propArr[smlroomctrl] = PSup[smlroomctrl]*curErrArr[SupplySmallRoom-1] + PTab[smlroomctrl]*curErrArr[Table3-1] + PCoolingWater[smlroomctrl]*curErrArr[ColdWaterSmallRoom]
        propArr[laserroomctrl] = PSup[laserroomctrl]*curErrArr[SupplyLaserRoom-1] + PTab[laserroomctrl]*curErrArr[Table4-1] + PCoolingWater[laserroomctrl]*curErrArr[ColdWaterLaserRoom]
        propArr[officectrl] = 0 #no control in office
        propArr = propArr - clip(propArr, -PropActionThreshold,PropActionThreshold)
    
        proprespArr = (P * propArr) # when used with arrays, * is component by component multiplcation or dot product for 1D arrays
    
        integArr =  zeros(ControlCh)
        integArr[bigroomctrl] = IntErrArr[Table1-1]
        integArr[smlroomctrl] = IntErrArr[Table3-1]
        integArr[laserroomctrl] = IntErrArr[Table4-1]
        integArr[officectrl] = 0 #no control in office
        integrespArr = (I * integArr) # when used with arrays, * is component by component multiplcation or dot product for 1D arrays
        #print integArr
        
        if((lastErrArr == zeros(Ch)).any()): #when the lastErrArr is the zero array, then don't do any diff because it's the first run
            diffrespArr = zeros(ControlCh)
        else:
            diffArr =  zeros(ControlCh)
            DiffErrArr = curErrArr - lastErrArr
            diffArr[bigroomctrl] = DiffErrArr[SupplyBigRoom-1] + ColdWaterDiffGain[bigroomctrl] * DiffErrArr[ColdWaterBigRoom-1] / D[bigroomctrl]
            diffArr[smlroomctrl] = DiffErrArr[SupplySmallRoom-1] + ColdWaterDiffGain[smlroomctrl] * DiffErrArr[ColdWaterSmallRoom-1] / D[smlroomctrl]
            diffArr[laserroomctrl] = DiffErrArr[SupplyLaserRoom-1] + ColdWaterDiffGain[laserroomctrl] * DiffErrArr[ColdWaterLaserRoom-1] / D[laserroomctrl]
            diffArr[officectrl] = 0 # no control in office
            diffArr = diffArr - clip(diffArr, -DiffActionThreshold,DiffActionThreshold)

            diffrespArr = (D * diffArr)
            diffrespArr = clip(diffrespArr, -DiffMax, DiffMax)
        
        responseArr = proprespArr + integrespArr + diffrespArr    
        return responseArr
            
    def CalcValveSignal(self,responseArr,curTempArr):#hard codes which control channel correspond to which output number
        valvesignalArr = zeros(ControlledValves)
    
        ColdWater = array([curTempArr[ColdWaterBigRoom-1], curTempArr[ColdWaterSmallRoom-1], curTempArr[ColdWaterLaserRoom-1],0 ])
        ColdWater = clip(ColdWater,0,20)
#        ColdWater = array([10,10,10,0]);   # set cold water temp to 10 degrees because the sensor is not working atm

        HotWater = array([curTempArr[HotWaterBigRoom-1], curTempArr[HotWaterSmallRoom-1], curTempArr[HotWaterLaserRoom-1], 0])
        SetPointAux = array([SetPoint[Table1-1], SetPoint[Table3-1], SetPoint[Table4-1], 0])  

        CoolingPower = clip(SetPointAux - ColdWater - ColdWaterTempCorrection,1,100) # estimate cooling power for valve settings, always assume some cooling power
        HeatingPower =  clip(HotWater - SetPointAux,20,200) # minum heating power corresponds to 20 degrees temp-difference

        ColdValveSignal = - responseArr/CoolingPower*ColdValveGain + Coldoffset + ColdWaterValveGain * (ColdWater-ColdWaterTempBase)
        HotValveSignal = Hotoffset + responseArr/HeatingPower*HotValveGain
        
                valvesignalArr[0] = ColdValveSignal[smlroomctrl]
                valvesignalArr[1] = HotValveSignal[smlroomctrl]
                valvesignalArr[2] = ColdValveSignal[bigroomctrl]
                valvesignalArr[3] = HotValveSignal[bigroomctrl]
                valvesignalArr[4] = ColdValveSignal[laserroomctrl]
                valvesignalArr[5] = HotValveSignal[laserroomctrl]
                valvesignalArr[6] = 0
                valvesignalArr[7] = 0

#                valvesignalArr[0] = clip(ColdValveSignal[smlroomctrl],ValveMin[0],ValveMax)
#                valvesignalArr[1] = clip(HotValveSignal[smlroomctrl],ValveMin[1],ValveMax)
#                valvesignalArr[2] = clip(ColdValveSignal[bigroomctrl],ValveMin[2],ValveMax)
#                valvesignalArr[3] = clip(HotValveSignal[bigroomctrl],ValveMin[3],ValveMax)
#                valvesignalArr[4] = clip(ColdValveSignal[laserroomctrl],ValveMin[4],ValveMax)
#                valvesignalArr[5] = clip(HotValveSignal[laserroomctrl],ValveMin[5],ValveMax)
#                valvesignalArr[6] = 0
#                valvesignalArr[7] = 0
    
        valvesignal = valvesignalArr.tolist()

        return valvesignalArr

class DataAcquisition():
    channels = 16
    hardwareGain = numpy.array([15,15,15,15,15,15,15,15,15,15,15,15,5,15,5,15]) #channels 13 and 15 (or 12,14 counting from 0) have less gain for expanded range
    V0 = 6.95 #volts on the voltage reference
    #dictionary of locations and corresponding array elements i.e table3 corresponds to hardwareGain[0]
    channelDict = {'Table1':7,
                   'Table2':4,
                   'Table3':0,
                   'Table4':5,
                   'Table5':8,
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
