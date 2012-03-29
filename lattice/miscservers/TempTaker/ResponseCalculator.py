import numpy

class ResponseCalculator():
    
    IntegrationMin = -2500.0 
    IntegrationMax = 3500.0
    controlCh = 3
    bigroomctrl, smlroomctrl, laserroomctrl = range(controlCh)
    valves = 2 * controlCh ####should not be needed her
    
    def __init__(self, channels, (P,I,D), setpoints, dict, integrator = None):
        self.lastError = numpy.zeros(channels)
        self.P = P
        self.I = I
        self.D = D
        self.setpoints = setpoints
        self.SupplyBigRoom = dict['SupplyBigRoom']
        self.SupplerLaserRoom = dict['SupplyLaserRoom']
        self.SupplySmallRoom = dict['SupplySmallRoom']
        self.Table1 = dict['Table1']
        self.Table3 = dict['Table3']
        self.Table4 = dict['Table4']
        self.ColdWater = dict['ColdWater']
        self.HotWater = dict['HotWater']       
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
        valveSignal = self.calcValveSignal(totalResponse, temp)
        self.lastError = errorSignal
        return propResponse, integResponse, diffResponse, totalResponse, valveSignal ####
                
    def calcIntegrator(self,old, new):
        total = old + new
        # Normalize maximum by the mean of the integration constants
        ####come back to this to translate from valve position
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
        ColdWater = 13.0 #can get from current temperatures, if available: ColdWater = array([curTempArr[ColdWaterBigRoom-1], curTempArr[ColdWaterSmallRoom-1], curTempArr[ColdWaterLaserRoom-1],0 ])ColdWater = clip(ColdWater,0,20)
        HotWater = temp[self.HotWater]
        SetPointAux = []
        
        coolingPower =  
        
            
    def calcValveSignal(self, totalResponse ,temp):
        valveSignal = numpy.zeros(self.valves)
        
        HotWater = temp[]

        HotWater = array([curTempArr[HotWaterBigRoom-1], curTempArr[HotWaterSmallRoom-1], curTempArr[HotWaterLaserRoom-1], 0])
        SetPointAux = array([SetPoint[Table1-1], SetPoint[Table3-1], SetPoint[Table4-1], 0])  

        CoolingPower = clip(SetPointAux - ColdWater,1,100) # estimate cooling power for valve settings, always assume some cooling power
        HeatingPower =  clip(HotWater - SetPointAux,20,200) # minum heating power corresponds to 20 degrees temp-difference

        ColdValveSignal = - responseArr/CoolingPower + Coldoffset + ColdWaterValveGain * (ColdWater-ColdWaterTempBase)
        HotValveSignal = Hotoffset + responseArr/HeatingPower
        
        valveSignal[0] = ColdValveSignal[smlroomctrl]
        valveSignal[1] = HotValveSignal[smlroomctrl]
        valveSignal[2] = ColdValveSignal[bigroomctrl]
        valveSignal[3] = HotValveSignal[bigroomctrl]
        valveSignal[4] = ColdValveSignal[laserroomctrl]
        valveSignal[5] = HotValveSignal[laserroomctrl]
        return valveSignal