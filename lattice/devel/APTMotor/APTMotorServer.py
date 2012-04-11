from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue
from ctypes import c_long, c_buffer, c_float, windll, pointer

class APTMotor():
    def __init__(self):
        self.aptdll = windll.LoadLibrary("C:\\APTDLLClient\\APT.dll")
        #self.aptdll.EnableEventDlg(False)
        self.aptdll.APTInit()
        print 'APT initialized'
        self.HWType = c_long(31) # 31 means TDC001 controller
    
    @inlineCallbacks
    def getNumberOfHardwareUnits(self):
        numUnits = c_long()
        yield self.aptdll.GetNumHWUnitsEx(self.HWType, pointer(numUnits))
        returnValue(numUnits.value)
    
    @inlineCallbacks
    def getSerialNumber(self, index):
        HWSerialNum = c_long()
        hardwareIndex = c_long(index)
        yield self.aptdll.GetHWSerialNumEx(self.HWType, hardwareIndex, pointer(HWSerialNum))
        returnValue(HWSerialNum.value)
    
    @inlineCallbacks
    def initializeHardwareDevice(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        yield self.aptdll.InitHWDevice(HWSerialNum)
        # need some kind of error reporting here
        returnValue(True)
        
    @inlineCallbacks
    def getHardwareInformation(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        model = c_buffer(255)
        softwareVersion = c_buffer(255)
        hardwareNotes = c_buffer(255)
        yield self.aptdll.GetHWInfo(HWSerialNum, model, 255, softwareVersion, 255, hardwareNotes, 255)      
        hwinfo = [model.value, softwareVersion.value, hardwareNotes.value]
        returnValue(hwinfo)
    
    @inlineCallbacks
    def getVelocityParameters(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        minimumVelocity = c_float()
        acceleration = c_float()
        maximumVelocity = c_float()
        yield self.aptdll.MOT_GetVelParams(HWSerialNum, pointer(minimumVelocity), pointer(acceleration), pointer(maximumVelocity))
        velocityParameters = [minimumVelocity.value, acceleration.value, maximumVelocity.value]
        returnValue(velocityParameters)
    
    @inlineCallbacks
    def setVelocityParameters(self, serialNumber, minVel, acc, maxVel):
        HWSerialNum = c_long(serialNumber)
        minimumVelocity = c_float(minVel)
        acceleration = c_float(acc)
        maximumVelocity = c_float(maxVel)
        yield self.aptdll.MOT_SetVelParams(HWSerialNum, minimumVelocity, acceleration, maximumVelocity)
        returnValue(True)
    
    @inlineCallbacks
    def getVelocityParameterLimits(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        maximumAcceleration = c_float()
        maximumVelocity = c_float()
        yield self.aptdll.MOT_GetVelParamLimits(HWSerialNum, pointer(maximumAcceleration), pointer(maximumVelocity))
        velocityParameterLimits = [maximumAcceleration.value, maximumVelocity.value]
        returnValue(velocityParameterLimits)    

    @inlineCallbacks
    def getPosition(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        position = c_float()
        yield self.aptdll.MOT_GetPosition(HWSerialNum, pointer(position))
        returnValue(position.value)    

    @inlineCallbacks
    def moveRelative(self, serialNumber, relDistance):
        HWSerialNum = c_long(serialNumber)
        relativeDistance = c_float(relDistance)
        yield self.aptdll.MOT_MoveRelativeEx(HWSerialNum, relativeDistance, True)
        returnValue(True)

    @inlineCallbacks
    def moveAbsolute(self, serialNumber, absPosition):
        HWSerialNum = c_long(serialNumber)
        absolutePosition = c_float(absPosition)
        yield self.aptdll.MOT_MoveAbsoluteEx(HWSerialNum, absolutePosition, True)
        returnValue(True)

    @inlineCallbacks
    def identify(self, serialNumber):
        HWSerialNum = c_long(serialNumber)
        yield self.aptdll.MOT_Identify(HWSerialNum)
        
    def cleanUpAPT(self):
        self.aptdll.APTCleanUp()
        print 'APT cleaned up'  

class APTMotorServer(LabradServer):
    """ Contains methods that interact with the APT motor controller """
    
    name = "APT Motor Server"
    
    onVelocityParameterChange = Signal(111111, 'signal: velocity parameter change', 'w')
    onPositionChange = Signal(222222, 'signal: position change', 'w')
    
    def initServer(self):
        self.aptMotor = APTMotor()        
        self.listeners = set()    
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified

    @setting(0, "Get Available Hardware Units", returns = '*w')
    def getAvailableHardwareUnits(self, c):
        """Returns a List of Available Hardware Units
            Index: Serial Number"""
        availableHardwareUnits = []
        numberOfHardwareUnits = yield self.aptMotor.getNumberOfHardwareUnits()
        for i in range(numberOfHardwareUnits):
            serialNumber = yield self.aptMotor.getSerialNumber(i)
            availableHardwareUnits.append(i)
            availableHardwareUnits.append(serialNumber)
        returnValue(availableHardwareUnits)

    @setting(1, "Initialize Hardware Device", serialNumber = 'w', returns ='b')
    def initializeHardwareDevice(self, c, serialNumber):
        """Initializes Hardware Device"""
        ok = yield self.aptMotor.initializeHardwareDevice(serialNumber)
        if (ok == True):
            c['Hardware Initialized'] = True
            returnValue(True)
        else:
            print 'false?'
            returnValue(False)
    
    @setting(2, "Get Device Information", serialNumber = 'w', returns ='*s')
    def getHardwareInformation(self, c, serialNumber):
        """Returns Hardware Information
            Model, Software Version, Hardware Notes"""
        if (c['Hardware Initialized'] == True):
            c['Hardware Information'] = yield self.aptMotor.getHardwareInformation(serialNumber)
            returnValue(c['Hardware Information'])


    @setting(3, "Get Velocity Parameters", serialNumber = 'w', returns ='*v')
    def getVelocityParameters(self, c, serialNumber):
        """Returns Velocity Parameters
            Minimum Velocity, Acceleration, Maximum Velocity"""
        if (c['Hardware Initialized'] == True):
            c['Velocity Parameters'] = yield self.aptMotor.getVelocityParameters(serialNumber)
            returnValue(c['Velocity Parameters'])

    @setting(4, "Get Velocity Parameter Limits", serialNumber = 'w', returns ='*v')
    def getVelocityParameterLimits(self, c, serialNumber):
        """Returns Velocity Parameter Limits
            Maximum Acceleration, Maximum Velocity"""
        if (c['Hardware Initialized'] == True):
            c['Velocity Parameter Limits'] = yield self.aptMotor.getVelocityParameterLimits(serialNumber)
            returnValue(c['Velocity Parameter Limits'])

    @setting(5, "Set Velocity Parameters", serialNumber = 'w', minimumVelocity = 'v', acceleration = 'v', maximumVelocity = 'v', returns ='b')
    def setVelocityParameters(self, c, serialNumber, minimumVelocity, acceleration, maximumVelocity):
        """Sets Velocity Parameters
            Minimum Velocity, Acceleration, Maximum Velocity"""
        if (c['Hardware Initialized'] == True):
            yield self.aptMotor.setVelocityParameters(serialNumber, minimumVelocity, acceleration, maximumVelocity)
            notified = self.getOtherListeners(c)
            self.onVelocityParameterChange(serialNumber, notified)
            returnValue(True)

    @setting(6, "Get Position", serialNumber = 'w', returns ='v')
    def getPosition(self, c, serialNumber):
        """Returns Current Position"""
        if (c['Hardware Initialized'] == True):
            c['Current Position'] = yield self.aptMotor.getPosition(serialNumber)
            returnValue(c['Current Position'])
        
    @setting(7, "Move Relative", serialNumber = 'w', relativeDistance = 'v', returns ='b')
    def moveRelative(self, c, serialNumber, relativeDistance):
        """Moves the Motor by a Distance Relative to its Current Position"""
        if (c['Hardware Initialized'] == True):
            yield self.aptMotor.moveRelative(serialNumber, relativeDistance)
            notified = self.getOtherListeners(c)
            self.onPositionChange(serialNumber, notified)
            returnValue(True)    

    @setting(8, "Move Absolute", serialNumber = 'w', absolutePosition = 'v', returns ='b')
    def moveAbsolute(self, c, serialNumber, absolutePosition):
        """Moves the Motor an Absolute Position"""
        if (c['Hardware Initialized'] == True):
            yield self.aptMotor.moveAbsolute(serialNumber, absolutePosition)
            notified = self.getOtherListeners(c)
            self.onPositionChange(serialNumber, notified)   
            returnValue(True)    

    @setting(9, "Identify Device", serialNumber = 'w', returns ='b')
    def identifyDevice(self, c, serialNumber):
        """Identifies Device by Flashing Front Panel LED for a Few Seconds"""
        if (c['Hardware Initialized'] == True):
            yield self.aptMotor.identify(serialNumber)
            returnValue(True)
    
    def stopServer( self ):  
        """Cleans up APT DLL before closing"""
        self.aptMotor.cleanUpAPT()
        
if __name__ == "__main__":
    from labrad import util
    util.runServer(APTMotorServer())