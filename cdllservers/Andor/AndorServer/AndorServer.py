from twisted.internet.defer import returnValue, DeferredLock
from twisted.internet.threads import deferToThread
#from AndorVideo import AndorVideo
#from PyQt4 import QtGui
#a = QtGui.QApplication( [] )
#import qt4reactor
#qt4reactor.install()   
from labrad.server import LabradServer, setting, Signal
from AndorCamera import AndorCamera
from labrad.units import WithUnit

#MR better arrange setting numbers

class AndorServer(LabradServer):
    """ Contains methods that interact with the Andor Luca"""
    
    name = "Andor Server"
    onKineticFinish = Signal(111111, 'signal: kinetic finish', 's')
    onAcquisitionEvent = Signal(222222, 'signal: acquisition event', 's')
    
    def initServer(self):
        self.listeners = set()
        self.camera = AndorCamera()
        self.lock = DeferredLock()
        
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified
    '''
    Temperature Related Settings
    '''
    @setting(0, "Get Temperature", returns = 'v[degC]')
    def get_temperature(self, c):
        """Gets Current Device Temperature"""
        temperature = None
        yield self.lock.acquire()
        try:
            temperature  = yield deferToThread(self.camera.get_temperature)
        finally:
            self.lock.release()
        if temperature is not None:
            temperature = WithUnit(temperature, 'degC')
            returnValue(temperature)

    @setting(1, "Get Cooler State", returns = 'b')
    def get_cooler_state(self, c):
        """Returns Current Cooler State"""
        cooler_state = None
        yield self.lock.acquire()
        try:
            cooler_state = yield deferToThread(self.camera.get_cooler_state)
        finally:
            self.lock.release()
        if cooler_state is not None:
            returnValue(cooler_state)
        
    @setting(3, "Set Temperature", setTemp = 'v[degC]', returns = '')
    def set_temperature(self, c, setTemp):
        """Sets The Target Temperature"""
        yield self.lock.acquire()
        try:
            yield deferToThread(self.camera.set_temperature, setTemp['degC'])
        finally:
            self.lock.release()
        
    @setting(23, "Set Cooler On", returns = '')
    def set_cooler_on(self, c):
        """Turns Cooler On"""
        yield self.lock.acquire()
        try:
            yield deferToThread(self.camera.set_cooler_on)
        finally:
            self.lock.release()
    
    @setting(24, "Set Cooler Off", returns = '')
    def set_cooler_off(self, c):
        """Turns Cooler On"""
        yield self.lock.acquire()
        try:
            yield deferToThread(self.camera.set_cooler_off)
        finally:
            self.lock.release()
    
    '''
    EMCCD Gain Settings
    '''     
    @setting(6, "Get EMCCD Gain", returns = 'i')
    def getEMCCDGain(self, c):
        """Gets Current EMCCD Gain"""
        gain = None
        yield self.lock.acquire()
        try:
            gain = yield deferToThread(self.camera.get_emccd_gain)
        finally:
            self.lock.release()
        if gain is not None:
            returnValue(gain)

    @setting(7, "Set EMCCD Gain", gain = 'i', returns = '')
    def setEMCCDGain(self, c, gain):
        """Sets Current EMCCD Gain"""
        yield self.lock.acquire()
        try:
            yield deferToThread(self.camera.set_emccd_gain, gain)
        finally:
            self.lock.release()
    '''
    Exposure Related Settings
    '''        
    @setting(8, "Get Read Mode", returns = 's')
    def getReadMode(self, c):
        return self.camera.get_read_mode()

    @setting(9, "Set Read Mode", readMode = 's', returns = '')
    def setReadMode(self, c, readMode):
        """Sets Current Read Mode"""
        mode = None
        yield self.lock.acquire()
        try:
            yield deferToThread(self.camera.set_read_mode, readMode)
        finally:
            self.lock.release()
        if mode is not None:
            returnValue(mode)
            
    @setting(10, "Get Acquisition Mode", returns = 's')
    def getAcquisitionMode(self, c):
        """Gets Current Acquisition Mode"""
        return self.camera.get_acquisition_mode()
        
    @setting(11, "Set Acquisition Mode", mode = 's', returns = '')
    def setAcquisitionMode(self, c, mode):
        """Sets Current Acquisition Mode"""
        yield self.lock.acquire()
        try:
            yield deferToThread(self.camera.set_acquisition_mode, mode)
        finally:
            self.lock.release()
            
            
        
    @setting(4, "Get Exposure Time", returns = 'v')
    def getExposureTime(self, c):
        """Gets Current Exposure Time"""
        c['Exposure Time'] = self.camera.exposureTime
        return c['Exposure Time']
    
    @setting(5, "Set Exposure Time", expTime = 'v', returns = 'v')
    def setExposureTime(self, c, expTime):
        """Sets Current Exposure Time"""
        yield deferToThread(self.camera.SetExposureTime, expTime)
        c['Exposure Time'] = self.camera.exposureTime
        returnValue(c['Exposure Time'])

    @setting(12, "Get Trigger Mode", returns = 'i')
    def getTriggerMode(self, c):
        """Gets Current Trigger Mode"""
        c['Trigger Mode'] = self.camera.triggerMode
        return c['Trigger Mode']
    
    @setting(13, "Set Trigger Mode", triggerMode = 'i', returns = 'i')
    def setTriggerMode(self, c, triggerMode):
        """Sets Current Trigger Mode"""
        yield deferToThread(self.camera.SetTriggerMode, triggerMode)
        c['Trigger Mode'] = self.camera.triggerMode
        returnValue(c['Trigger Mode'])

    @setting(14, "Get Image Region", returns = '*i')
    def getImageRegion(self, c):
        """Gets Current Image Region"""
        c['Image Region'] = self.camera.imageRegion
        return c['Image Region']
        
    @setting(15, "Set Image Region", horizontalBinning = 'i', verticalBinning = 'i', horizontalStart = 'i', horizontalEnd = 'i', verticalStart = 'i', verticalEnd = 'i', returns = '*i')
    def setImageRegion(self, c, horizontalBinning, verticalBinning, horizontalStart, horizontalEnd, verticalStart, verticalEnd):
        """Sets Current Image Region"""
        yield deferToThread(self.camera.SetImage, horizontalBinning, verticalBinning, horizontalStart, horizontalEnd, verticalStart, verticalEnd)
        c['Image Region'] = self.camera.imageRegion
        self.camera.setDimensions((horizontalEnd - horizontalStart + 1), (verticalEnd - verticalStart + 1))
        returnValue(c['Image Region'])
        
    @setting(16, "Get Camera Serial Number", returns = 'i')
    def getCameraSerialNumber(self, c):
        """Gets Camera Serial Number"""
        yield deferToThread(self.camera.GetCameraSerialNumber)
        c['Serial Number'] = self.camera.serial
        returnValue(c['Serial Number'])
    
    @setting(17, "Get Number Kinetics", returns = 'i')
    def getNumberKinetics(self, c):
        """Gets Number Of Scans In A Kinetic Cycle"""
        c['Number Kinetics'] = self.camera.numberKinetics
        return c['Number Kinetics']
    
    @setting(18, "Set Number Kinetics", numKin = 'i', returns = 'i')
    def setNumberKinetics(self, c, numKin):
        """Sets Number Of Scans In A Kinetic Cycle"""
        yield deferToThread(self.camera.SetNumberKinetics, numKin)
        c['Number Kinetics'] = self.camera.numberKinetics
        returnValue(c['Number Kinetics'])

    @setting(19, "Get Kinetic Cycle Time", returns = 'v')
    def getKineticCycleTime(self, c):
        """Gets Time Between Kinetic Cycles"""
        c['Kinetic Cycle Time'] = self.camera.kineticCycleTime
        return c['Kinetic Cycle Time']
    
    @setting(20, "Set Kinetic Cycle Time", kinCycleTime = 'v', returns = 'v')
    def setKineticCycleTime(self, c, kinCycleTime):
        """Sets Time Between Kinetic Cycles"""
        yield deferToThread(self.camera.SetKineticCycleTime, kinCycleTime)
        c['Kinetic Cycle Time'] = self.camera.numberKinetics
        returnValue(c['Kinetic Cycle Time'])

    @setting(21, "Get Status", returns = 's')
    def getStatus(self, c):
        """Gets Current Camera Status"""
        yield deferToThread(self.camera.GetStatus)
        c['Status'] = self.camera.status
        returnValue(c['Status'])

    @setting(22, "Get Series Progress", returns = 'w')
    def getSeriesProgress(self, c):
        """Gets Current Scan In Series"""
        yield deferToThread(self.camera.GetSeriesProgress)
        c['Series Progress'] = self.camera.seriesProgress
        returnValue(c['Series Progress'])
    
    @setting(25, "Get Most Recent Image", returns = '*i')
    def getMostRecentImage(self, c):
        """Gets Most Recent Image"""
        #yield deferToThread(self.camera.GetMostRecentImage)
        imageArray = yield deferToThread(self.camera.GetMostRecentImage)
        #returnValue(self.camera.imageArray)
        returnValue(imageArray)
        
    @setting(26, "Wait For Acquisition", returns = 's')
    def waitForAcquisition(self, c):
        error = yield deferToThread(self.camera.WaitForAcquisition)
        returnValue(error)

    @setting(27, "Get Acquired Data", returns = '*i')
    def getAcquiredData(self, c):
        """Get all Data"""
        yield deferToThread(self.camera.GetAcquiredData)
        returnValue(self.camera.singleImageArray)

    @setting(28, "Save As Text", path = 's', returns = '')
    def saveAsText(self, c, path):
        """Saves Current Image As A Text File"""
        yield deferToThread(self.camera.SaveAsTxt, path) 
        
    @setting(29, "Start Acquisition", returns = '')
    def startAcquisition(self, c):
        yield deferToThread(self.camera.StartAcquisition)
        print 'starting acquisition: DRV_SUCCESS'
    
    @setting(30, "Get Detector Dimensions", returns = '*i')
    def getDetectorDimensions(self, c):
        c['Detector Dimensions'] = self.camera.detectorDimensions
        returnValue(c['Detector Dimensions'])
       
    @setting(31, "Get Acquired Data Kinetic", numKin = 'i', returns = '')
    def getAcquiredDataKinetic(self, c, numKin):
        """Get all Data for a Number of Scans"""
        yield deferToThread(self.camera.GetAcquiredDataKinetic, numKin)
#        returnValue(self.camera.imageArray)

    @setting(32, "Start Acquisition Kinetic", numKin = 'i', returns = '')
    def startAcquisitionKinetic(self, c, numKin):
        yield deferToThread(self.camera.StartAcquisitionKinetic, numKin)
        self.onKineticFinish("Number Scans: {0}".format(numKin), self.listeners)
            #not sure yet

    @setting(33, "Save As Text Kinetic", path = 's', kinSet = 'i', numKin = 'i', returns = '')
    def saveAsTextKinetic(self, c, path, kinSet, numKin):
        """Saves a Series of Images As Text Files"""
        yield deferToThread(self.camera.SaveAsTxtKinetic, path, kinSet, numKin) 

    @setting(34, "Open As Text", path = 's', returns = '')
    def openAsText(self, c, path):
        """Opens a Text File as Image"""
        yield deferToThread(self.camera.OpenAsTxt, path) 
    
    @setting(35, "Open As Text Kinetic", path = 's', kinSet = 'i', numKin = 'i', returns = '')
    def openAsTextKinetic(self, c, path, kinSet, numKin):
        """Opens a Series of Text Files As Images"""
        yield deferToThread(self.camera.OpenAsTxtKinetic, path, kinSet, numKin) 

    @setting(36, "Start Acquisition Kinetic External", returns = '')
    def startAcquisitionKineticExternal(self, c):
        yield deferToThread(self.camera.StartAcquisitionKineticExternal)

    @setting(37, "Save To Data Vault", directory = 's', name = 's', returns = '')
    def saveToDataVault(self, c, directory, name):
        """Save Current Single Image To Data Vault"""
        directory = list(eval(directory))
        yield deferToThread(self.camera.SaveToDataVault, directory, name) 

    @setting(38, "Save To Data Vault Kinetic", directory = 's', name = 's', numKin = 'i', returns = '')
    def saveToDataVaultKinetic(self, c, directory, name, numKin):
        """Saves a Series of Images As Text Files"""
        directory = list(eval(directory))
        yield self.camera.SaveToDataVaultKinetic(directory, name, numKin) 

    @setting(39, "Open From Data Vault", directory = 's', dataset = 'i', returns = '')
    def openFromDataVault(self, c, directory, dataset):
        """Opens a Single Image From Data Vault"""
        directory = list(eval(directory))
        yield deferToThread(self.camera.OpenFromDataVault, directory, dataset) 

    @setting(40, "Open From Data Vault Kinetic", directory = 's', numKin = 'i', returns = '')
    def openFromDataVaultKinetic(self, c, directory, numKin):
        """Opens a Series of Images From Data Vault"""
        directory = list(eval(directory))
        print 'dir: ', directory
        yield self.camera.OpenFromDataVaultKinetic(directory, numKin) 
    
    @setting(41, "Clear Image Array", returns = '')
    def clearImageArray(self, c):
        yield deferToThread(self.camera.ClearImageArray)             

    @setting(98, "Abort Acquisition", returns = 's')
    def abortAcquisition(self, c):
        error = yield deferToThread(self.camera.AbortAcquisition)
        returnValue(error)
   
    def stopServer(self):  
        """Shuts down camera before closing"""
        self.camera.shut_down()

if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorServer())