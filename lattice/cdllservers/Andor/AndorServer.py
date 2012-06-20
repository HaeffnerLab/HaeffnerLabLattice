from ctypes import *
import time
from PIL import Image
import sys
import numpy as np
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from labrad.server import LabradServer, setting

"""Andor class which is meant to provide the Python version of the same
   functions that are defined in the Andor's SDK. Since Python does not
   have pass by reference for immutable variables, some of these variables
   are actually stored in the class instance. For example the temperature,
   gain, gainRange, status etc. are stored in the class. """

class Andor:
    def __init__(self):
        #cdll.LoadLibrary("/usr/local/lib/libandor.so")
        #self.dll = CDLL("/usr/local/lib/libandor.so")
        #error = self.dll.Initialize("/usr/local/etc/andor/")
        self.dll = windll.LoadLibrary(r'C:\Users\lattice\Desktop\LabRAD\lattice\cdllservers\Andor\atmcd32d.dll')
        error = self.dll.Initialize(r'C:\Users\lattice\Desktop\LabRAD\lattice\cdllservers\Andor')

        cw = c_int()
        ch = c_int()
        self.dll.GetDetector(byref(cw), byref(ch))

        self.width              = cw.value
        self.height             = ch.value
        self.coolerState        = 0 # Off
        self.currentTemperature = None
        self.setTemperature     = -20
        self.EMCCDGain          = 0
        self.verbosity          = True
        self.preampgain         = None
        self.channel            = None
        self.outamp             = None
        self.hsspeed            = None
        self.vsspeed            = None
        self.serial             = ''
        self.seriesProgress     = 0
        self.exposureTime       = .1 # seconds
        self.accumulate         = None
        self.kinetic            = None
        self.numberKinetics     = 1
        self.kineticCycleTime   = 0.01
        self.readMode           = 4
        self.acquisitionMode    = 1
        self.triggerMode        = 0
#        self.horizontalBinning = 1
#        self.verticalBinning   = 1
#        self.horizontalStart   = 1
#        self.horizontalEnd     = self.width
#        self.verticalStart     = 1
#        self.verticalEnd       = self.height
        self.imageRegion        = [1, 1, 1, self.width, 1, self.height]
        #self.imageArray         = np.zeros((self.height * self.width))
        

    def __del__(self):
        error = self.dll.ShutDown()
    
    def verbose(self, error, function=''):
        print "[%s]: %s" %(function, error)
        # usage: self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)

    def SetVerbose(self, state=True):
        self.verbose = state

    def setDimensions(self, width, height):
        self.width = width
        self.height = height
    
    def AbortAcquisition(self):
        error = self.dll.AbortAcquisition()
        return ERROR_CODE[error]

    def ShutDown(self):
        error = self.dll.ShutDown()
        return ERROR_CODE[error]
            
    def GetCameraSerialNumber(self):
        serial = c_int()
        error = self.dll.GetCameraSerialNumber(byref(serial))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.serial = serial.value      
        return ERROR_CODE[error]
    
    def SetReadMode(self, readMode):
        error = self.dll.SetReadMode(readMode)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.readMode = readMode      
        return ERROR_CODE[error]
    
    def SetAcquisitionMode(self, acquisitionMode):
        error = self.dll.SetAcquisitionMode(acquisitionMode)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.acquisitionMode = acquisitionMode      
        return ERROR_CODE[error]
        
    def SetNumberKinetics(self, numKin):
        error = self.dll.SetNumberKinetics(numKin)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.numberKinetics = numKin      
        return ERROR_CODE[error]
                  
    def SetKineticCycleTime(self, time):
        error = self.dll.SetKineticCycleTime(c_float(time))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.kineticCycleTime = time      
        return ERROR_CODE[error]

    def SetImage(self, hbin, vbin, hstart, hend, vstart, vend):
        error = self.dll.SetImage(hbin, vbin, hstart, hend, vstart, vend)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.imageRegion = [hbin, vbin, hstart, hend, vstart, vend]
        return ERROR_CODE[error]

    def StartAcquisition(self):
        error = self.dll.StartAcquisition()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.dll.WaitForAcquisition()
        return ERROR_CODE[error]

    def WaitForAcquisition(self):
        error = self.dll.WaitForAcquisition()
        return ERROR_CODE[error]
    
    def GetAcquiredData(self,imageArray,numKin=1):  
        dim = self.width * self.height * numKin
        cimageArray = c_int * dim
        cimage = cimageArray()
        #self.dll.WaitForAcquisition()
        error = self.dll.GetAcquiredData(pointer(cimage),dim)
        print ERROR_CODE[error]
        self.imageArray = cimage[:]

        return ERROR_CODE[error]
    
    def GetMostRecentImage(self):
        #self.dll.WaitForAcquisition()
        dim = self.width * self.height
        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self.dll.GetMostRecentImage(pointer(cimage),dim)
        self.imageArray = cimage[:]
        return ERROR_CODE[error]        

    def SetExposureTime(self, time):
        error = self.dll.SetExposureTime(c_float(time))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.exposureTime = time        
        return ERROR_CODE[error]
        
    def SetSingleScan(self):
        self.SetReadMode(4)
        self.SetAcquisitionMode(1)
        self.SetImage(1,1,1,self.width,1,self.height)


        im.save(path,"BMP")

    def SaveAsTxt(self, path):
                     
        file = open(path, 'w')
        
        # self.imageArray is 1 dimensional!
        count = 1
        for i in self.imageArray:
            file.write(str(int(i)))
            count += 1
            if (count == self.height):
                file.write("\n")
                count = 0
            else:
                file.write(' ')

        file.close()

    def getCoolerState(self):
        cCoolerState = c_int()
        error = self.dll.IsCoolerOn(byref(cCoolerState))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.coolerState = cCoolerState.value      
        return ERROR_CODE[error]
    
    def CoolerON(self):
        error = self.dll.CoolerON()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.coolerState = 1
        return ERROR_CODE[error]

    def CoolerOFF(self):
        error = self.dll.CoolerOFF()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.coolerState = 0
        return ERROR_CODE[error]

    def GetCurrentTemperature(self):
        ctemperature = c_int()
        error = self.dll.GetTemperature(byref(ctemperature))
        if (ERROR_CODE[error] == 'DRV_TEMP_STABILIZED' or ERROR_CODE[error] == 'DRV_TEMP_NOT_REACHED' or ERROR_CODE[error] == 'DRV_TEMP_DRIFT' or ERROR_CODE[error] == 'DRV_TEMP_NOT_STABILIZED'):
            self.currentTemperature = ctemperature.value
        return ERROR_CODE[error]

    def SetTemperature(self,temperature):
        error = self.dll.SetTemperature(temperature)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.setTemperature = temperature
        return ERROR_CODE[error]
    
    def GetEMCCDGain(self):
        gain = c_int()
        error = self.dll.GetEMCCDGain(byref(gain))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.EMCCDGain = gain.value      
        return ERROR_CODE[error]
        
    def SetEMCCDGain(self, gain):
        error = self.dll.SetEMCCDGain(gain)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.EMCCDGain = gain             
        return ERROR_CODE[error]
        
    def SetTriggerMode(self, mode):
        error = self.dll.SetTriggerMode(mode)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.triggerMode = mode
        return ERROR_CODE[error]
    
    def GetStatus(self):
        status = c_int()
        error = self.dll.GetStatus(byref(status))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.status = ERROR_CODE[status.value]      
        return ERROR_CODE[error]
        
    def GetSeriesProgress(self):
        acc = c_long()
        series = c_long()
        error = self.dll.GetAcquisitionProgress(byref(acc),byref(series))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            self.seriesProgress = series.value
        return ERROR_CODE[error]
    
#    def GetAcquisitionTimings(self):
#        exposure   = c_float()
#        accumulate = c_float()
#        kinetic    = c_float()
#        error = self.dll.GetAcquisitionTimings(byref(exposure),byref(accumulate),byref(kinetic))
#        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#            return [exposure.value, accumulate.value, kinetic.value]      
#        else:
#            return [sys._getframe().f_code.co_name, ERROR_CODE[error]]
#
#    def SetNumberAccumulations(self, number):
#        error = self.dll.SetNumberAccumulations(number)
#        return [sys._getframe().f_code.co_name, ERROR_CODE[error]]
#            
#    def SetAccumulationCycleTime(self, time):
#        error = self.dll.SetAccumulationCycleTime(c_float(time))
#        return [sys._getframe().f_code.co_name, ERROR_CODE[error]]
#
#    def SetShutter(self, typ, mode, closingtime, openingtime):
#        error = self.dll.SetShutter(typ, mode, closingtime, openingtime)
#        return [sys._getframe().f_code.co_name, ERROR_CODE[error]]
#
#    def SetCoolerMode(self, mode):
#        error = self.dll.SetCoolerMode(mode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#
#    def SaveAsBmp(self, path):
#        im=Image.new("RGB",(self.height,self.width),"white")
#        #im=Image.new("RGB",(512,512),"white")
#        pix = im.load()
#        for i in range(len(self.imageArray)):
#            (row, col) = divmod(i,self.width)
#            picvalue = int(round(self.imageArray[i]*255.0/65535))
#            pix[row,col] = (picvalue,picvalue,picvalue)
#            
#    def SetEMCCDGainMode(self, gainMode):
#        error = self.dll.SetEMCCDGainMode(gainMode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]   
#    def SetImageRotate(self, iRotate):
#        error = self.dll.SetImageRotate(iRotate)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#
#    def SaveAsBmpNormalised(self, path):
#
#        im=Image.new("RGB",(512,512),"white")
#        pix = im.load()
#
#        maxIntensity = max(self.imageArray)
#
#        for i in range(len(self.imageArray)):
#            (row, col) = divmod(i,self.width)
#            picvalue = int(round(self.imageArray[i]*255.0/maxIntensity))
#            pix[row,col] = (picvalue,picvalue,picvalue)
#
#        im.save(path,"BMP")
#        
#    def SaveAsFITS(self, filename, type):
#        error = self.dll.SaveAsFITS(filename, type)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#
#
#             
#    def GetAccumulationProgress(self):
#        acc = c_long()
#        series = c_long()
#        error = self.dll.GetAcquisitionProgress(byref(acc),byref(series))
#        if ERROR_CODE[error] == "DRV_SUCCESS":
#            return acc.value
#        else:
#            return None
#
#    def SetEMAdvanced(self, gainAdvanced):
#        error = self.dll.SetEMAdvanced(gainAdvanced)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#
#    def GetEMGainRange(self):
#        low = c_int()
#        high = c_int()
#        error = self.dll.GetEMGainRange(byref(low),byref(high))
#        self.gainRange = (low.value, high.value)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#      
#    def GetNumberADChannels(self):
#        noADChannels = c_int()
#        error = self.dll.GetNumberADChannels(byref(noADChannels))
#        self.noADChannels = noADChannels.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#
#    def GetBitDepth(self):
#        bitDepth = c_int()
#
#        self.bitDepths = []
#
#        for i in range(self.noADChannels):
#            self.dll.GetBitDepth(i,byref(bitDepth))
#            self.bitDepths.append(bitDepth.value)
#
#    def SetADChannel(self, index):
#        error = self.dll.SetADChannel(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.channel = index
#        return ERROR_CODE[error]  
#        
#    def SetOutputAmplifier(self, index):
#        error = self.dll.SetOutputAmplifier(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.outamp = index
#        return ERROR_CODE[error]
#        
#    def GetNumberHSSpeeds(self):
#        noHSSpeeds = c_int()
#        error = self.dll.GetNumberHSSpeeds(self.channel, self.outamp, byref(noHSSpeeds))
#        self.noHSSpeeds = noHSSpeeds.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#
#    def GetHSSpeed(self):
#        HSSpeed = c_float()
#
#        self.HSSpeeds = []
#
#        for i in range(self.noHSSpeeds):
#            self.dll.GetHSSpeed(self.channel, self.outamp, i, byref(HSSpeed))
#            self.HSSpeeds.append(HSSpeed.value)
#            
#    def SetHSSpeed(self, index):
#        error = self.dll.SetHSSpeed(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.hsspeed = index
#        return ERROR_CODE[error]
#        
#    def GetNumberVSSpeeds(self):
#        noVSSpeeds = c_int()
#        error = self.dll.GetNumberVSSpeeds(byref(noVSSpeeds))
#        self.noVSSpeeds = noVSSpeeds.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#
#    def GetVSSpeed(self):
#        VSSpeed = c_float()
#
#        self.VSSpeeds = []
#
#        for i in range(self.noVSSpeeds):
#            self.dll.GetVSSpeed(i,byref(VSSpeed))
#            self.preVSpeeds.append(VSSpeed.value)
#
#    def SetVSSpeed(self, index):
#        error = self.dll.SetVSSpeed(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.vsspeed = index
#        return ERROR_CODE[error] 
#    
#    def GetNumberPreAmpGains(self):
#        noGains = c_int()
#        error = self.dll.GetNumberPreAmpGains(byref(noGains))
#        self.noGains = noGains.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#
#    def GetPreAmpGain(self):
#        gain = c_float()
#
#        self.preAmpGain = []
#
#        for i in range(self.noGains):
#            self.dll.GetPreAmpGain(i,byref(gain))
#            self.preAmpGain.append(gain.value)
#
#    def SetPreAmpGain(self, index):
#        error = self.dll.SetPreAmpGain(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.preampgain = index
#        return ERROR_CODE[error]
#        
#    def SetFrameTransferMode(self, frameTransfer):
#        error = self.dll.SetFrameTransferMode(frameTransfer)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#        
#    def SetShutterEx(self, typ, mode, closingtime, openingtime, extmode):
#        error = self.dll.SetShutterEx(typ, mode, closingtime, openingtime, extmode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
#        
#    def SetSpool(self, active, method, path, framebuffersize):
#        error = self.dll.SetSpool(active, method, c_char_p(path), framebuffersize)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

class AndorServer(LabradServer):
    """ Contains methods that interact with the Andor Luca"""
    
    name = "Andor Server"
    
    def initServer(self):

        self.listeners = set()  
        self.prepareCamera()

    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified

    def prepareCamera(self):
        self.camera = Andor()
#        camera.SetSingleScan()
#        camera.SetTriggerMode(TriggerMode)
#        camera.SetPreAmpGain(PreAmpGain)
#        camera.SetEMCCDGain(EMCCDGain)
#        camera.SetExposureTime(ExposureTime)
#        camera.CoolerON()        
        
#        if stabilise is True:
#            print "Stabilising the temperature..."
#            if not cam.IsCoolerOn():
#                cam.CoolerON()
#            while cam.GetTemperature() is not 'DRV_TEMP_STABILIZED':
#                print "Temperature is: %g [Set T: %g, %s]" % (cam.temperature, Tset, cam.GetTemperature())
#                time.sleep(10)

    # doesn't return temp
    @setting(0, "Get Current Temperature", returns = '*s')
    def getCurrentTemperature(self, c):
        """Gets Current Device Temperature"""
        error = yield deferToThread(self.camera.GetCurrentTemperature)
        if (error == 'DRV_TEMP_STABILIZED' or error == 'DRV_TEMP_NOT_REACHED' or error == 'DRV_TEMP_DRIFT' or error == 'DRV_TEMP_NOT_STABILIZED'):
            c['Current Temperature'] = self.camera.currentTemperature
            returnValue([str(c['Current Temperature']), error])
        else:
            raise Exception(error)

    # doesn't like booleans, turn it to 'ON' or 'OFF'
    @setting(1, "Get Cooler State", returns = 'i')
    def getCoolerState(self, c):
        """Returns Current Cooler State"""
        error = yield deferToThread(self.camera.getCoolerState)
        if (error == 'DRV_SUCCESS'):
            c['Cooler State'] = self.camera.coolerState
            returnValue(c['Cooler State'])
        else:
            raise Exception(error)
    
    @setting(2, "Set Cooler State", returns = '?')
    def setCoolerState(self, c):
        """The Luca Is Always Cooled To -20C"""
        
    @setting(3, "Set Temperature", setTemp = 'i', returns = 'i')
    def setTemperature(self, c, setTemp):
        """Sets The Target Temperature"""
        error = yield deferToThread(self.camera.SetTemperature, setTemp)
        if (error == 'DRV_SUCCESS'):
            c['Set Temperature'] = self.camera.setTemperature
            returnValue(c['Set Temperature'])
        else:
            raise Exception(error)

    @setting(4, "Get Exposure Time", returns = 'v')
    def getExposureTime(self, c):
        """Gets Current Exposure Time"""
        c['Exposure Time'] = self.camera.exposureTime
        return c['Exposure Time']
    
    @setting(5, "Set Exposure Time", expTime = 'v', returns = 'v')
    def setExposureTime(self, c, expTime):
        """Sets Current Exposure Time"""
        error = yield deferToThread(self.camera.SetExposureTime, expTime)
        if (error == 'DRV_SUCCESS'):
            c['Exposure Time'] = self.camera.exposureTime
            returnValue(c['Exposure Time'])
        else:
            raise Exception(error)
        
    @setting(6, "Get EMCCD Gain", returns = 'i')
    def getEMCCDGain(self, c):
        """Gets Current EMCCD Gain"""
        error = yield deferToThread(self.camera.GetEMCCDGain)
        if (error == 'DRV_SUCCESS'):
            c['EMCCD Gain'] = self.camera.EMCCDGain
            returnValue(c['EMCCD Gain'])
        else:
            raise Exception(error)
    
    @setting(7, "Set EMCCD Gain", gain = 'i', returns = 'i')
    def setEMCCDGain(self, c, gain):
        """Sets Current EMCCD Gain"""
        error = yield deferToThread(self.camera.SetEMCCDGain, gain)
        if (error == 'DRV_SUCCESS'):
            c['EMCCD Gain'] = self.camera.EMCCDGain
            returnValue(c['EMCCD Gain'])
        else:
            raise Exception(error)
        
    @setting(8, "Get Read Mode", returns = 'i')
    def getReadMode(self, c):
        """Gets Current Read Mode"""
        c['Read Mode'] = self.camera.readMode
        return c['Read Mode']
    
    @setting(9, "Set Read Mode", readMode = 'i', returns = 'i')
    def setReadMode(self, c, readMode):
        """Sets Current Read Mode"""
        error = yield deferToThread(self.camera.SetReadMode, readMode)
        if (error == 'DRV_SUCCESS'):
            c['Read Mode'] = self.camera.readMode
            returnValue(c['Read Mode'])
        else:
            raise Exception(error)
 
    @setting(10, "Get Acquisition Mode", returns = 'i')
    def getAcquisitionMode(self, c):
        """Gets Current Acquisition Mode"""
        c['Acquisition Mode'] = self.camera.acquisitionMode
        return c['Acquisition Mode']
    
    @setting(11, "Set Acquisition Mode", acqMode = 'i', returns = 'i')
    def setAcquisitionMode(self, c, acqMode):
        """Sets Current Acquisition Mode"""
        error = yield deferToThread(self.camera.SetAcquisitionMode, acqMode)
        if (error == 'DRV_SUCCESS'):
            c['Acquisition Mode'] = self.camera.acquisitionMode
            returnValue(c['Acquisition Mode'])
        else:
            raise Exception(error)

    @setting(12, "Get Trigger Mode", returns = 'i')
    def getTriggerMode(self, c):
        """Gets Current Trigger Mode"""
        c['Trigger Mode'] = self.camera.triggerMode
        return c['Trigger Mode']
    
    @setting(13, "Set Trigger Mode", triggerMode = 'i', returns = 'i')
    def setTriggerMode(self, c, triggerMode):
        """Sets Current Trigger Mode"""
        error = yield deferToThread(self.camera.SetTriggerMode, triggerMode)
        if (error == 'DRV_SUCCESS'):
            c['Trigger Mode'] = self.camera.triggerMode
            returnValue(c['Trigger Mode'])
        else:
            raise Exception(error)
    
    @setting(14, "Get Image Region", returns = '*i')
    def getImageRegion(self, c):
        """Gets Current Image Region"""
        c['Image Region'] = self.camera.imageRegion
        return c['Image Region']
        
    
    @setting(15, "Set Image Region", horizontalBinning = 'i', verticalBinning = 'i', horizontalStart = 'i', horizontalEnd = 'i', verticalStart = 'i', verticalEnd = 'i', returns = '*i')
    def setImageRegion(self, c, horizontalBinning, verticalBinning, horizontalStart, horizontalEnd, verticalStart, verticalEnd):
        """Sets Current Image Region"""
        error = yield deferToThread(self.camera.SetImage, horizontalBinning, verticalBinning, horizontalStart, horizontalEnd, verticalStart, verticalEnd)
        if (error == 'DRV_SUCCESS'):
            c['Image Region'] = self.camera.imageRegion
            self.camera.setDimensions((horizontalEnd - horizontalStart + 1), (verticalEnd - verticalStart + 1))
            returnValue(c['Image Region'])
        else:
            raise Exception(error)
        
    @setting(16, "Get Camera Serial Number", returns = 'i')
    def getCameraSerialNumber(self):
        """Gets Camera Serial Number"""
        error = yield deferToThread(self.camera.GetCameraSerialNumber)
        if (error == 'DRV_SUCCESS'):
            c['Serial Number'] = self.camera.serial
            returnValue(c['Serial Number'])
        else:
            raise Exception(error)
    
    @setting(17, "Get Number Kinetics", returns = 'i')
    def getNumberKinetics(self, c):
        """Gets Number Of Scans In A Kinetic Cycle"""
        c['Number Kinetics'] = self.camera.numberKinetics
        return c['Number Kinetics']
    
    @setting(18, "Set Number Kinetics", numKin = 'i', returns = 'i')
    def setNumberKinetics(self, c, numKin):
        """Sets Number Of Scans In A Kinetic Cycle"""
        error = yield deferToThread(self.camera.SetNumberKinetics, numKin)
        if (error == 'DRV_SUCCESS'):
            c['Number Kinetics'] = self.camera.numberKinetics
            returnValue(c['Number Kinetics'])
        else:
            raise Exception(error)

    @setting(19, "Get Kinetic Cycle Time", returns = 'v')
    def getKineticCycleTime(self, c):
        """Gets Time Between Kinetic Cycles"""
        c['Kinetic Cycle Time'] = self.camera.kineticCycleTime
        return c['Kinetic Cycle Time']
    
    @setting(20, "Set Kinetic Cycle Time", kinCycleTime = 'v', returns = 'v')
    def setKineticCycleTime(self, c, kinCycleTime):
        """Sets Time Between Kinetic Cycles"""
        error = yield deferToThread(self.camera.SetKineticCycleTime, kinCycleTime)
        if (error == 'DRV_SUCCESS'):
            c['Kinetic Cycle Time'] = self.camera.numberKinetics
            returnValue(c['Kinetic Cycle Time'])
        else:
            raise Exception(error)
   
    @setting(21, "Get Status", returns = 's')
    def getStatus(self, c):
        """Gets Current Camera Status"""
        error = yield deferToThread(self.camera.GetStatus)
        if (error == 'DRV_SUCCESS'):
            c['Status'] = self.camera.status
            returnValue(c['Status'])
        else:
            raise Exception(error)
    
    @setting(22, "Get Series Progress", returns = 'w')
    def getSeriesProgress(self, c):
        """Gets Current Scan In Series"""
        error = yield deferToThread(self.camera.GetSeriesProgress)
        if (error == 'DRV_SUCCESS'):
            c['Series Progress'] = self.camera.seriesProgress
            returnValue(c['Series Progress'])
        else:
            raise Exception(error)

    @setting(23, "Cooler ON", returns = 's')
    def coolerON(self, c):
        """Turns Cooler On"""
        error = yield deferToThread(self.camera.CoolerON)
        returnValue(error)
        
    @setting(24, "Cooler OFF", returns = 's')
    def coolerOFF(self, c):
        """Turns Cooler On"""
        error = yield deferToThread(self.camera.CoolerOFF)
        returnValue(error)        
    
    @setting(25, "Get Most Recent Image", returns = '*i')
    def getMostRecentImage(self, c):
        """Gets Most Recent Image"""
        error = yield deferToThread(self.camera.GetMostRecentImage)
        if (error == 'DRV_SUCCESS'):
            returnValue(self.camera.imageArray)
        else:
            print error
            raise Exception(error)
        
    @setting(26, "Wait For Acquisition", returns = 's')
    def waitForAcquisition(self, c):
        error = yield deferToThread(self.camera.WaitForAcquisition)
        returnValue(error)

    @setting(27, "Get Acquired Data", numKin = 'i', returns = '*i')
    def getAcquiredData(self, c, numKin=1):
        """Gets Most Recent Scan"""
        error = yield deferToThread(self.camera.GetAcquiredData, numKin)
        if (error == 'DRV_SUCCESS'):
            returnValue(self.camera.imageArray)
        else:
            raise Exception(error)

    @setting(28, "Save As Text", path = 's', returns = '')
    def saveAsText(self, c, path):
        """Saves Current Image As A Text File"""
        error = yield deferToThread(self.camera.SaveAsTxt(path)) 
        
    @setting(29, "Start Acquisition", returns = 's')
    def startAcquisition(self, c):
        error = yield deferToThread(self.camera.StartAcquisition)
        print 'starting acquisition: ', error
        returnValue(error)

    @setting(98, "Abort Acquisition", returns = 's')
    def abortAcquisition(self, c):
        error = yield deferToThread(self.camera.AbortAcquisition)
        returnValue(error)

    @setting(99, "Shutdown", returns = 's')
    def shutdown(self, c):
        error = yield deferToThread(self.camera.ShutDown)
        returnValue(error)
    
    def stopServer(self):  
        """Shuts down camera before closing"""
        error = yield deferToThread(self.camera.ShutDown)


ERROR_CODE = {
    20001: "DRV_ERROR_CODES",
    20002: "DRV_SUCCESS",
    20003: "DRV_VXNOTINSTALLED",
    20006: "DRV_ERROR_FILELOAD",
    20007: "DRV_ERROR_VXD_INIT",
    20010: "DRV_ERROR_PAGELOCK",
    20011: "DRV_ERROR_PAGE_UNLOCK",
    20013: "DRV_ERROR_ACK",
    20024: "DRV_NO_NEW_DATA",
    20026: "DRV_SPOOLERROR",
    20034: "DRV_TEMP_OFF",
    20035: "DRV_TEMP_NOT_STABILIZED",
    20036: "DRV_TEMP_STABILIZED",
    20037: "DRV_TEMP_NOT_REACHED",
    20038: "DRV_TEMP_OUT_RANGE",
    20039: "DRV_TEMP_NOT_SUPPORTED",
    20040: "DRV_TEMP_DRIFT",
    20050: "DRV_COF_NOTLOADED",
    20053: "DRV_FLEXERROR",
    20066: "DRV_P1INVALID",
    20067: "DRV_P2INVALID",
    20068: "DRV_P3INVALID",
    20069: "DRV_P4INVALID",
    20070: "DRV_INIERROR",
    20071: "DRV_COERROR",
    20072: "DRV_ACQUIRING",
    20073: "DRV_IDLE",
    20074: "DRV_TEMPCYCLE",
    20075: "DRV_NOT_INITIALIZED",
    20076: "DRV_P5INVALID",
    20077: "DRV_P6INVALID",
    20083: "P7_INVALID",
    20089: "DRV_USBERROR",
    20091: "DRV_NOT_SUPPORTED",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}

if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorServer())