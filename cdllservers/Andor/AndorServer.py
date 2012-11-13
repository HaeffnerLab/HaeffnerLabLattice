from ctypes import *
import time
import sys
import numpy as np
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from AndorVideo import AndorVideo
from PyQt4 import QtGui
#a = QtGui.QApplication( [] )
#import qt4reactor
#qt4reactor.install()   
from labrad.server import LabradServer, setting, Signal


"""Andor class which is meant to provide the Python version of the same
   functions that are defined in the Andor's SDK. Since Python does not
   have pass by reference for immutable variables, some of these variables
   are actually stored in the class instance. For example the temperature,
   gain, gainRange, status etc. are stored in the class. """

class Andor:
    def __init__(self, parent):
        #cdll.LoadLibrary("/usr/local/lib/libandor.so")
        #self.dll = CDLL("/usr/local/lib/libandor.so")
        #error = self.dll.Initialize("/usr/local/etc/andor/")
        
        self.parent = parent
        
        self.dll = windll.LoadLibrary(r'C:\Users\lattice\Desktop\LabRAD\lattice\cdllservers\Andor\atmcd32d.dll')
        error = self.dll.Initialize(r'C:\Users\lattice\Desktop\LabRAD\lattice\cdllservers\Andor')

        cw = c_int()
        ch = c_int()
        self.dll.GetDetector(byref(cw), byref(ch))

        self.detectorDimensions = [cw.value, ch.value]
        self.width              = self.detectorDimensions[0]
        self.height             = self.detectorDimensions[1]
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
        self.imageArray         = []
        self.singleImageArray   = []
        self.currentImageArray  = []
        self.openVideoWindow()
        
    def openVideoWindow(self):
        self.andorVideo = AndorVideo(self)

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
        print 'SHUTDOWN succeeded'
        return ERROR_CODE[error]
            
    def GetCameraSerialNumber(self):
        serial = c_int()
        error = self.dll.GetCameraSerialNumber(byref(serial))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.serial = serial.value      
        else:
            raise Exception(ERROR_CODE[error])
    
    def SetReadMode(self, readMode):
        error = self.dll.SetReadMode(readMode)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.readMode = readMode      
        else:
            raise Exception(ERROR_CODE[error])
    
    def SetAcquisitionMode(self, acquisitionMode):
        error = self.dll.SetAcquisitionMode(acquisitionMode)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.acquisitionMode = acquisitionMode      
        else:
            raise Exception(ERROR_CODE[error])
                
    def SetNumberKinetics(self, numKin):
        error = self.dll.SetNumberKinetics(numKin)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.numberKinetics = numKin      
        else:
            raise Exception(ERROR_CODE[error])
                  
    def SetKineticCycleTime(self, time):
        error = self.dll.SetKineticCycleTime(c_float(time))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.kineticCycleTime = time      
        else:
            raise Exception(ERROR_CODE[error])

    def SetImage(self, hbin, vbin, hstart, hend, vstart, vend):
        error = self.dll.SetImage(hbin, vbin, hstart, hend, vstart, vend)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.hstart = hstart
            self.hend = hend
            self.vstart = vstart
            self.vend = vend
            self.setDimensions((hend - hstart + 1), (vend - vstart + 1))
            self.imageRegion = [hbin, vbin, hstart, hend, vstart, vend]
        else:
            raise Exception(ERROR_CODE[error])

    def StartAcquisition(self):
        error = self.dll.StartAcquisition()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            errorWait = self.dll.WaitForAcquisition()
            if (ERROR_CODE[errorWait] == 'DRV_SUCCESS'):
                pass
            else:
                raise Exception(ERROR_CODE[errorWait])                
        else:
            raise Exception(ERROR_CODE[error])

    def StartAcquisitionKinetic(self, numKin):
        cnt = 0
        error = self.dll.StartAcquisition()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            # WaitForAcquisition finishes after ONE image is finished, this for loop will ensure
            # that this method will wait for all images to be taken.
            for i in range(numKin):
                errorWait = self.dll.WaitForAcquisition()
                if (ERROR_CODE[errorWait] != 'DRV_SUCCESS'):
                    raise Exception(ERROR_CODE[errorWait])
                cnt += 1
                self.parent.onAcquisitionEvent("Acquired: {0} of {1}".format(cnt, numKin), self.parent.listeners)
                print "Acquired: {0} of {1}".format(cnt, numKin)                                
        else:
            raise Exception(ERROR_CODE[error])
        
    def StartAcquisitionKineticExternal(self):
        error = self.dll.StartAcquisition()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            pass
        else:
            raise Exception(ERROR_CODE[error])

    def WaitForAcquisition(self):
        error = self.dll.WaitForAcquisition()
        return ERROR_CODE[error]
    
    def GetAcquiredData(self):  
        dim = self.width * self.height
        cimageArray = c_int * dim
        cimage = cimageArray()
        #self.dll.WaitForAcquisition()
        error = self.dll.GetAcquiredData(pointer(cimage),dim)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            imageArray = cimage[:]
            self.currentSingleImageArray = imageArray
            self.singleImageArray.append(imageArray)
            del imageArray
        else:
            raise Exception(ERROR_CODE[error])        
    
    def GetAcquiredDataKinetic(self, numKin):  
        dim = self.width * self.height * numKin
        cimageArray = c_int * dim
        cimage = cimageArray()
        #self.dll.WaitForAcquisition()
        error = self.dll.GetAcquiredData(pointer(cimage),dim)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.currentImageArray = cimage[:]
            self.imageArray.append(cimage[:])
            print 'acquired kinetic!'
        else:
            raise Exception(ERROR_CODE[error]) 
   
    def GetMostRecentImage(self):
        #self.dll.WaitForAcquisition()
        dim = self.width * self.height
        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self.dll.GetMostRecentImage(pointer(cimage),dim)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            #self.imageArray = cimage[:]
            return cimage[:]
        else:
            raise Exception(ERROR_CODE[error])

    def SetExposureTime(self, time):
        error = self.dll.SetExposureTime(c_float(time))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.exposureTime = time        
        else:
            raise Exception(ERROR_CODE[error])
        
    def SetSingleScan(self):
        self.SetReadMode(4)
        self.SetAcquisitionMode(1)
        self.SetImage(1,1,1,self.width,1,self.height)


    def SaveAsTxt(self, path):
                     
        file = open(path, 'w')
        
        # self.imageArray is 1 dimensional!
        count = 0
        for i in self.imageArray:
            file.write(str(int(i)))
            count += 1
            if (count == self.height):
                file.write("\n")
                count = 0
            else:
                file.write(' ')

        file.close()
        
        #np.savetxt(path, np.reshape(self.imageArray, (self.height, self.width)))
        
    def SaveAsTxtKinetic(self, path, kinSet, numKin):
#        # split up the image array into an array of arrays
#        # ASSUMES CURRENT WIDTH AND HEIGHT ARE CORRECT FOR THE IMAGE!!!
#        print 'from saveastxtkinetc numKin: ', numKin
#        print 'from saveastxtkinetic len(imarray): ', len(self.imageArray)
#        imageArray = np.reshape(self.imageArray, (numKin, 1, (len(self.imageArray)/numKin)))
#        cnt = 0
#        for image in np.arange(numKin):
#            file = open(path + str(cnt), 'w')
#            
#            # self.imageArray is 1 dimensional!
#            count = 0
#            for i in imageArray[image][0]:
#                file.write(str(int(i)))
#                count += 1
#                if (count == self.width):
#                    file.write("\n")
#                    count = 0
#                else:
#                    file.write(' ')
#
#            file.close()
#            cnt += 1
        
         """ saving scheme: name-kinSet-numKin
                        Ex: image-1-1
                        Ex: image-1-27
         """
        
         imageArray = np.reshape(self.currentImageArray, (numKin, self.height, self.width))
         for image in np.arange(numKin):
             np.savetxt(path+'-'+str(kinSet+1)+'-'+str(image+1), imageArray[image], fmt='%d')           
            
    def OpenAsTxt(self, path):
        self.singleImageArray = np.ravel(np.loadtxt(path)) 
        
    def OpenAsTxtKinetic(self, path, kinSet, numKin):
        """Assumes a series of txt files with a consecutive numbers appended to the end. Ex: image1, image2, image3..etc. 
            
            image12 means kinetic set 1, image 2
            image122 means kinetic set 1, image 22
            
            The image array returned is 1 dimensional, with the images in sequential order. The images are sliced into rows.
            
            Ex: 2 sets of 3 images of size (2 rows, 3 cols)
                array of shape: (2, 3, 2, 3) -> (36)
                
                
        
            """
        self.imageArray = []
        imageArray = [[] for i in np.arange(numKin)]
        for kinSetNumber in np.arange(kinSet):
            for imageNumber in np.arange(numKin):
                imageArray[imageNumber] = np.loadtxt(path+'-'+str(kinSetNumber + 1)+'-'+str(imageNumber+1))
#            imageArray = np.array(imageArray)
            self.imageArray.append(np.ravel(np.array(imageArray))) #since labRAD doesn't like to transfer around multidimensional arrays (sorry!)
        del imageArray
        
    @inlineCallbacks
    def SaveToDataVault(self, directory, name):
        dv = self.parent.client.data_vault
        t1 = time.clock() 
        width = np.arange(self.width + 1) + 1
        height = np.arange(self.height + 1) + 1

        lenWidth = len(width)
        lenHeight = len(height)

        Width = np.ravel([width]*lenHeight)
        Height = []
        for i in height:
            Height.append([i]*lenWidth)
        Height = np.ravel(np.array(Height))
        
        yield dv.cd(directory)
#        yield self.cxn.data_vault.new('Half-Life', [('x', 'in')], [('y','','in')])         
#        yield self.cxn.data_vault.add([[0.0,0.2],[1.0,0.2],[2.4,2.3],[3.3,0.0],[4.7,0.4],[4.5,1.2],[3.8,1.0],[2.3,4.8],[1.1,4.8],[1.1,4.1],[1.7,4.1],[2.0,3.4],[0.0,0.2]] )

        yield dv.new(name, [('Pixels', '')], [('Pixels','',''), ('Counts','','')])    

         
        toDataVault = np.array(np.vstack((Height, Width, self.currentSingleImageArray)).transpose(), dtype=float)
        yield dv.add(toDataVault)
        t2 = time.clock()
        print 'time for an image of size : ', (self.width + 1), (self.height + 1), (t2-t1), ' sec'
        print 'saved!'        

    @inlineCallbacks
    def SaveToDataVaultKinetic(self, directory, name, numKin):
        dv = self.parent.client.data_vault
        print len(self.currentImageArray)
        print self.height
        print self.width
        print numKin
        imageArray = np.reshape(self.currentImageArray, (numKin, 1, (self.height * self.width))) # needs to be currentImageArray!!!
        for image in np.arange(numKin):
            t1 = time.clock() 
            print 'width: ', (self.width)
            print 'height: ', (self.height)
            width = np.arange(self.width) + 1
            height = np.arange(self.height) + 1
    
            lenWidth = len(width)
            lenHeight = len(height)
    
            Width = np.ravel([width]*lenHeight)
            Height = []
            for i in height:
                Height.append([i]*lenWidth)
            Height = np.ravel(np.array(Height))
            
            yield dv.cd(directory, True)
    #        yield self.cxn.data_vault.new('Half-Life', [('x', 'in')], [('y','','in')])         
    #        yield self.cxn.data_vault.add([[0.0,0.2],[1.0,0.2],[2.4,2.3],[3.3,0.0],[4.7,0.4],[4.5,1.2],[3.8,1.0],[2.3,4.8],[1.1,4.8],[1.1,4.1],[1.7,4.1],[2.0,3.4],[0.0,0.2]] )
            yield dv.new(name, [('Pixels', '')], [('Pixels','',''), ('Counts','','')])      
            print 'Height: ', len(Height)
            print 'Width: ', len(Width)
            print 'shape: ', imageArray[image].shape   
            yield dv.add_parameter('hstart', self.hstart)
            yield dv.add_parameter('hend', self.hend)         
            yield dv.add_parameter('vstart', self.vstart)
            yield dv.add_parameter('vend', self.vend)
            toDataVault = np.array(np.vstack((Height, Width, imageArray[image])).transpose(), dtype=float)
            print toDataVault
            yield dv.add(toDataVault)
            t2 = time.clock()
            print 'time for an image of size : ', (self.width + 1), (self.height + 1), (t2-t1), ' sec'
            print 'saved!' 
    
    @inlineCallbacks
    def OpenFromDataVault(self, directory, dataset):
        dv = self.parent.client.data_vault
        yield dv.cd(directory)
        yield dv.open(dataset)
        Data = yield dv.get()
        data = Data.asarray
        zData = np.array([None]*len(data))
        for i in np.arange(len(data)):
            zData[i] = data[i][2]
            
        self.singleImageArray = zData       
        
    
    @inlineCallbacks
    def OpenFromDataVaultKinetic(self, directory, numKin):
        dv = self.parent.client.data_vault
        yield dv.cd(directory)
        for i in np.arange(numKin):
            yield dv.open(int(i+1))
            Data = yield dv.get()
            data = Data.asarray
            print data
            print 'lendata: ', len(data)
            zData = np.array([None]*len(data))
            for j in np.arange(len(data)):
                zData[j] = data[j][2]
                
            self.imageArray.append(zData)
            print 'done!'            
    
    def getCoolerState(self):
        cCoolerState = c_int()
        error = self.dll.IsCoolerOn(byref(cCoolerState))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.coolerState = cCoolerState.value      
        else:
            raise Exception(ERROR_CODE[error])
    
    def CoolerON(self):
        error = self.dll.CoolerON()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.coolerState = 1
        else:
            raise Exception(ERROR_CODE[error])

    def CoolerOFF(self):
        error = self.dll.CoolerOFF()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.coolerState = 0
        else:
            raise Exception(ERROR_CODE[error])

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
        else:
            raise Exception(ERROR_CODE[error])
    
    def GetEMCCDGain(self):
        gain = c_int()
        error = self.dll.GetEMCCDGain(byref(gain))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.EMCCDGain = gain.value      
        else:
            raise Exception(ERROR_CODE[error])
        
    def SetEMCCDGain(self, gain):
        error = self.dll.SetEMCCDGain(gain)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.EMCCDGain = gain             
        else:
            raise Exception(ERROR_CODE[error])
        
    def SetTriggerMode(self, mode):
        error = self.dll.SetTriggerMode(mode)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.triggerMode = mode
        else:
            raise Exception(ERROR_CODE[error])
    
    def GetStatus(self):
        status = c_int()
        error = self.dll.GetStatus(byref(status))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.status = ERROR_CODE[status.value]      
        else:
            raise Exception(ERROR_CODE[error])
        
    def GetSeriesProgress(self):
        acc = c_long()
        series = c_long()
        error = self.dll.GetAcquisitionProgress(byref(acc),byref(series))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            self.seriesProgress = series.value
        else:
            raise Exception(ERROR_CODE[error])
    
    def ClearImageArray(self):
        self.imageArray = []
    
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

    onKineticFinish = Signal(111111, 'signal: kinetic finish', 's')
    onAcquisitionEvent = Signal(222222, 'signal: acquisition event', 's')
    
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
        self.camera = Andor(self)
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
        yield deferToThread(self.camera.getCoolerState)
        c['Cooler State'] = self.camera.coolerState
        returnValue(c['Cooler State'])

    
    @setting(2, "Set Cooler State", returns = '?')
    def setCoolerState(self, c):
        """The Luca Is Always Cooled To -20C"""
        
    @setting(3, "Set Temperature", setTemp = 'i', returns = 'i')
    def setTemperature(self, c, setTemp):
        """Sets The Target Temperature"""
        yield deferToThread(self.camera.SetTemperature, setTemp)
        c['Set Temperature'] = self.camera.setTemperature
        returnValue(c['Set Temperature'])

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
        
    @setting(6, "Get EMCCD Gain", returns = 'i')
    def getEMCCDGain(self, c):
        """Gets Current EMCCD Gain"""
        yield deferToThread(self.camera.GetEMCCDGain)
        c['EMCCD Gain'] = self.camera.EMCCDGain
        returnValue(c['EMCCD Gain'])

    
    @setting(7, "Set EMCCD Gain", gain = 'i', returns = 'i')
    def setEMCCDGain(self, c, gain):
        """Sets Current EMCCD Gain"""
        yield deferToThread(self.camera.SetEMCCDGain, gain)
        c['EMCCD Gain'] = self.camera.EMCCDGain
        returnValue(c['EMCCD Gain'])

        
    @setting(8, "Get Read Mode", returns = 'i')
    def getReadMode(self, c):
        """Gets Current Read Mode"""
        c['Read Mode'] = self.camera.readMode
        return c['Read Mode']
    
    @setting(9, "Set Read Mode", readMode = 'i', returns = 'i')
    def setReadMode(self, c, readMode):
        """Sets Current Read Mode"""
        yield deferToThread(self.camera.SetReadMode, readMode)
        c['Read Mode'] = self.camera.readMode
        returnValue(c['Read Mode'])

    @setting(10, "Get Acquisition Mode", returns = 'i')
    def getAcquisitionMode(self, c):
        """Gets Current Acquisition Mode"""
        c['Acquisition Mode'] = self.camera.acquisitionMode
        return c['Acquisition Mode']
    
    @setting(11, "Set Acquisition Mode", acqMode = 'i', returns = 'i')
    def setAcquisitionMode(self, c, acqMode):
        """Sets Current Acquisition Mode"""
        yield deferToThread(self.camera.SetAcquisitionMode, acqMode)
        c['Acquisition Mode'] = self.camera.acquisitionMode
        returnValue(c['Acquisition Mode'])

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

    @setting(23, "Cooler ON", returns = '')
    def coolerON(self, c):
        """Turns Cooler On"""
        yield deferToThread(self.camera.CoolerON)
        
    @setting(24, "Cooler OFF", returns = '')
    def coolerOFF(self, c):
        """Turns Cooler On"""
        yield deferToThread(self.camera.CoolerOFF)
    
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

    @setting(99, "Shutdown", returns = 's')
    def shutdown(self, c):
        error = yield deferToThread(self.camera.ShutDown)
        returnValue(error)
    
    def stopServer(self):  
        """Shuts down camera before closing"""
        error = self.camera.ShutDown()
        print error


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