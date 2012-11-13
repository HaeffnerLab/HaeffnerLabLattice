import numpy

class ResponseCalculator():
    
    IntegrationMin = -2500.0 
    IntegrationMax = 3500.0
    controlCh = 3
    bigroomctrl, smlroomctrl, laserroomctrl = range(controlCh)
    valves = 2 * controlCh 
    Coldoffset = numpy.array([65,35,45]) #adding an offset because the valve seems to open only at around 50 [big,sml,laser]
    Hotoffset = numpy.array([67,70,70])
    coldWaterValveGain = numpy.array([0.1, 0.2, 0.2]) #adds some value  (ColdWaterValveGain * (ActualColdWater-ColdWaterTempBase)) to the cold valve depending on the cold water tempererature deviation from ColdWaterTempBase, [big,sml, laser]
    
    def __init__(self, channels, (P,I,D), setpoints, channels, integrator = None):
        self.lastError = numpy.zeros(channels)
        self.P = P
        self.I = I
        self.D = D
        self.setpoints = setpoints
        self.SupplyBigRoom = channels['SupplyBigRoom']
        self.SupplerLaserRoom = channels['SupplyLaserRoom']
        self.SupplySmallRoom = channels['SupplySmallRoom']
        self.Table1 = channels['Table1']
        self.Table3 = channels['Table3']
        self.Table4 = channels['Table4']
        self.ColdWater = channels['ColdWater']
        self.HotWater = channels['HotWater']       
        if integrator is None: 
            self.integralError = numpy.zeros(channels)
        else:
            self.integralError = integrator
    
    def updateGains(self, (P,I,D)):
        #constants for PID in the format [big room , small room , laser room]
        self.P = P
        self.I = I
        self.D = D
    
    def getResponse(self, temp):
        errorSignal = temp - self.setpoints
        self.integralError =  self.calcIntegrator(self.integralError, errorSignal)
        propResponse, integResponse, diffResponse, totalResponse = self.findPIDresponse(errorSignal, self.integralError , self.lastError)
        valveSignal = self.adjustOnPower(totalResponse, temp)
        self.lastError = errorSignal
        return propResponse, integResponse, diffResponse, totalResponse, valveSignal
                
    def calcIntegrator(self,old, new):
        total = old + new
        # Normalize maximum by the mean of the integration constants
        minim = self.IntegrationMin/(-sum(self.I)/len(self.I))
        maxim = self.IntegrationMax/(-sum(self.I)/len(self.I))
        total = numpy.clip(total,minim,maxim)
        return total
            
    def findPIDresponse(self, errorSignal, integralError, lastError):    
        #P Gain is calculated based on the supply air temperature to account for fast changes
        propArr = numpy.zeros(self.controlCh)
        propArr[self.bigroomctrl] = errorSignal[self.SupplyBigRoom]#in case of cold water temp: + PCoolingWater[bigroomctrl]*errorSignal[ColdWaterBigRoom]
        propArr[self.smlroomctrl] = errorSignal[self.SupplySmallRoom]# + PCoolingWater[smlroomctrl]*curErrArr[ColdWaterSmallRoom]
        propArr[self.laserroomctrl] = errorSignal[self.SupplyLaserRoom]# + PTab[laserroomctrl]*curErrArr[Table4-1] + PCoolingWater[laserroomctrl]*curErrArr[ColdWaterLaserRoom]
        propResponse = self.P * propArr
        #I Gain
        integArr =  numpy.zeros(self.controlCh)
        integArr[self.bigroomctrl] = integralError[self.Table1]
        integArr[self.smlroomctrl] = integralError[self.Table3]
        integArr[self.laserroomctrl] = integralError[self.Table4]
        integResponse = (self.I * integArr) 
        #D Gain, seems to work well with no D gain
        diffResponse = numpy.zeros(self.ControlCh) 
        #Total
        totalResponse = propResponse + integResponse + diffResponse    
        return propResponse, integResponse, diffResponse, totalResponse
    
    def adjustOnPower(self, totalResponse, temp):
        '''adjusts the gains based on the current cooling and heating powers, derived from the cooling and heating water temperatures'''
        coldWaterTemp = 13.0 #can get from current temperatures, if available: ColdWater = array([curTempArr[ColdWaterBigRoom-1], curTempArr[ColdWaterSmallRoom-1], curTempArr[ColdWaterLaserRoom-1],0 ])ColdWater = clip(ColdWater,0,20)
        hotWaterTemp = temp[self.HotWater]
        setPoint = numpy.array(self.setpoints[self.Table1], self.setpoints[self.Table3], self.setpoints[self.Table4])
        coolingPower =  numpy.clip(setPoint - coldWaterTemp, 1.0, 100.0)
        heatingPower = numpy.clip(hotWaterTemp - setPoint, 20.0, 200.0)
        coldValveSignal = -totalResponse/coolingPower + self.coldOffset + self.coldWaterValveGain * (coldWaterTemp-self.setpoints[self.ColdWater])
        hotValveSignal = self.hotOffset + totalResponse/heatingPower
        valveSignal = numpy.zeros(self.valves)
        valveSignal[0] = coldValveSignal[self.smlroomctrl]
        valveSignal[1] = hotValveSignal[self.smlroomctrl]
        valveSignal[2] = coldValveSignal[self.bigroomctrl]
        valveSignal[3] = hotValveSignal[self.bigroomctrl]
        valveSignal[4] = coldValveSignal[self.laserroomctrl]
        valveSignal[5] = hotValveSignal[self.laserroomctrl]
        return valveSignal