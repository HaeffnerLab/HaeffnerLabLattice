import ctypes as c
from configuration import andor_configuration as config
import os

class AndorInfo(object):
    
    def __init__(self):
        self.width                  = None
        self.height                 = None
        self.min_temp               = None
        self.max_temp               = None
        self.cooler_state           = None
        self.temperature_setpoint   = None
        self.temperature            = None
        self.serial_number          = None
        self.min_gain               = None
        self.max_gain               = None
        self.emccd_gain             = None
        self.read_mode              = None
        self.acquisition_mode       = None
        self.trigger_mode           = None
#         self.preampgain         = None
#         self.channel            = None
#         self.outamp             = None
#         self.hsspeed            = None
#         self.vsspeed            = None
#         self.serial             = ''
#         self.seriesProgress     = 0
#         self.exposureTime       = .1 # seconds
#         self.accumulate         = None
#         self.kinetic            = None
#         self.numberKinetics     = 1
#         self.kineticCycleTime   = 0.01


#         
#         self.imageRegion        = [1, 1, 1, None, 1, None]
#         self.imageArray         = []
#         self.singleImageArray   = []
#         self.currentImageArray  = []


               
class AndorCamera(object):
    """
    Andor class which is meant to provide the Python version of the same
    functions that are defined in the Andor's SDK. Since Python does not
    have pass by reference for immutable variables, some of these variables
    are actually stored in the class instance. For example the temperature,
    gain, gainRange, status etc. are stored in the class.
    """
    
    def __init__(self):
        try:
            print 'Loading DLL'
            self.dll = c.windll.LoadLibrary(config.path_to_dll)
            print 'Initializing Camera'
            error = self.dll.Initialize(os.path.dirname(__file__))
            print 'Done Initializing, {}'.format(ERROR_CODE[error])
            self.info = AndorInfo()
            self.get_detector_dimensions()
            self.get_temperature_range()
            self.get_camera_serial_number()
            self.get_camera_em_gain_range()
            self.get_emccd_gain()
            self.set_read_mode(config.read_mode)
            self.set_acquisition_mode(config.acquisition_mode)
            self.set_cooler_on()
            self.set_temperature(config.set_temperature)
            self.get_cooler_state()
            self.get_temperature()
        except Exception as e:
            print 'Error Initializing Camera', e

    def print_get_software_version(self):
        '''
        gets the version of the SDK
        '''
        eprom = c.c_int()
        cofFile = c.c_int()
        vxdRev = c.c_int()
        vxdVer = c.c_int()
        dllRev = c.c_int()
        dllVer = c.c_int()
        self.dll.GetSoftwareVersion(c.byref(eprom), c.byref(cofFile), c.byref(vxdRev), c.byref(vxdVer),  c.byref(dllRev), c.byref(dllVer))
        print 'Software Version'
        print eprom
        print cofFile
        print vxdRev
        print vxdVer
        print dllRev
        print dllVer
        
    def print_get_capabilities(self):
        '''
        gets the exact capabilities of the camera
        '''
        
        class AndorCapabilities(c.Structure):
            _fields_ = [('ulSize', c.c_ulong),
                        ('ulAcqModes', c.c_ulong),
                        ('ulReadModes', c.c_ulong),
                        ('ulTriggerModes', c.c_ulong),
                        ('ulCameraType', c.c_ulong),
                        ('ulPixelMode', c.c_ulong),
                        ('ulSetFunctions', c.c_ulong),
                        ('ulGetFunctions', c.c_ulong),
                        ('ulFeatures', c.c_ulong),
                        ('ulPCICard', c.c_ulong),
                        ('ulEMGainCapability', c.c_ulong),
                        ('ulFTReadModes', c.c_ulong),
                        ]
        caps = AndorCapabilities()
        caps.ulSize = c.c_ulong(c.sizeof(caps))
        error = self.dll.GetCapabilities(c.byref(caps))
        print 'ulAcqModes',         '{:07b}'.format(caps.ulAcqModes)
        print 'ulReadModes',        '{:06b}'.format(caps.ulReadModes)
        print 'ulTriggerModes',     '{:08b}'.format(caps.ulTriggerModes)
        print 'ulCameraType',       '{}'.format(caps.ulCameraType)
        print 'ulPixelMode',        '{:032b}'.format(caps.ulPixelMode)
        print 'ulSetFunctions',     '{:025b}'.format(caps.ulSetFunctions)
        print 'ulGetFunctions',     '{:016b}'.format(caps.ulGetFunctions)
        print 'ulFeatures',         '{:020b}'.format(caps.ulFeatures)
        print 'ulPCICard',          '{}'.format(caps.ulPCICard)
        print 'ulEMGainCapability', '{:020b}'.format(caps.ulEMGainCapability)
        print 'ulFTReadModes',      '{:06b}'.format(caps.ulFTReadModes)
        
    def get_detector_dimensions(self):
        '''
        gets the dimensions of the detector
        '''
        detector_width = c.c_int()
        detector_height = c.c_int()
        self.dll.GetDetector(c.byref(detector_width), c.byref(detector_height))
        self.info.width = detector_width.value
        self.info.height = detector_height.value
        return [self.info.width, self.info.height]
        
    def get_temperature_range(self):
        '''
        gets the range of available temperatures
        '''
        min_temp = c.c_int()
        max_temp = c.c_int()
        self.dll.GetTemperatureRange(c.byref(min_temp), c.byref(max_temp))
        self.info.min_temp = min_temp.value
        self.info.max_temp = max_temp.value
        return [self.info.min_temp, self.info.max_temp]
        
    def get_cooler_state(self):
        '''
        reads the state of the cooler
        '''
        cooler_state = c.c_int()
        error = self.dll.IsCoolerOn(c.byref(cooler_state))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.cooler_state = bool(cooler_state)
            return self.info.cooler_state
        else:
            raise Exception(ERROR_CODE[error])
        
    def set_cooler_on(self):
        '''
        turns on cooling
        '''
        error = self.dll.CoolerON()
        if not (ERROR_CODE[error] == 'DRV_SUCCESS'):
            raise Exception(ERROR_CODE[error])

    def set_cooler_off(self):
        '''
        turns off cooling
        '''
        error = self.dll.CoolerOFF()
        if not (ERROR_CODE[error] == 'DRV_SUCCESS'):
            raise Exception(ERROR_CODE[error])

    def get_temperature(self):
        temperature = c.c_int()
        error = self.dll.GetTemperature(c.byref(temperature))
        if (ERROR_CODE[error] == 'DRV_TEMP_STABILIZED' or ERROR_CODE[error] == 'DRV_TEMP_NOT_REACHED' or ERROR_CODE[error] == 'DRV_TEMP_DRIFT' or ERROR_CODE[error] == 'DRV_TEMP_NOT_STABILIZED'):
            self.info.temperature = temperature.value
            return temperature.value
        else:
            raise Exception(ERROR_CODE[error])

    def set_temperature(self, temperature):
        temperature = c.c_int(int(temperature))
        error = self.dll.SetTemperature( temperature )
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.temperature_setpoint = temperature.value
        else:
            raise Exception(ERROR_CODE[error])
        
    def get_camera_serial_number(self):
        serial_number = c.c_int()
        error = self.dll.GetCameraSerialNumber(c.byref(serial_number))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.serial_number = serial_number.value  
        else:
            raise Exception(ERROR_CODE[error])
    
    def get_camera_em_gain_range(self):
        min_gain = c.c_int()
        max_gain = c.c_int()
        error = self.dll.GetEMGainRange(c.byref(min_gain), c.byref(max_gain))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.min_gain = min_gain.value
            self.info.max_gain = max_gain.value
        else:
            raise Exception(ERROR_CODE[error])
        
    def get_emccd_gain(self):
        gain = c.c_int()
        error = self.dll.GetEMCCDGain(c.byref(gain))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.emccd_gain = gain.value
            return gain.value
        else:
            raise Exception(ERROR_CODE[error])
        
    def set_emccd_gain(self, gain):
        error = self.dll.SetEMCCDGain(c.c_int(int(gain)))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.emccd_gain = gain             
        else:
            raise Exception(ERROR_CODE[error])
    
    def set_read_mode(self, mode):
        try:
            mode_number = READ_MODE[mode]
        except KeyError:
            raise Exception("Incorrect read mode {}".format(mode))
        error = self.dll.SetReadMode(c.c_int(mode_number))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.read_mode = mode      
        else:
            raise Exception(ERROR_CODE[error])
    
    def get_read_mode(self):
        return self.info.read_mode
    
    def set_acquisition_mode(self, mode):
        try:
            mode_number = AcquisitionMode[mode]
        except KeyError:
            raise Exception("Incorrect acquisition mode {}".format(mode))
        error = self.dll.SetAcquisitionMode(c.c_int(mode_number))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.acquisition_mode = mode      
        else:
            raise Exception(ERROR_CODE[error])
    
    def get_acquisition_mode(self):
        return self.info.acquisition_mode
    
    def set_trigger_mode(self, mode):
        error = self.dll.SetTriggerMode(mode)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.triggerMode = mode
        else:
            raise Exception(ERROR_CODE[error])
    
        
#     #MR?
#     def setDimensions(self, width, height):
#         self.width = width
#         self.height = height
#     
#     def AbortAcquisition(self):
#         error = self.dll.AbortAcquisition()
#         return ERROR_CODE[error]

#     def SetNumberKinetics(self, numKin):
#         error = self.dll.SetNumberKinetics(numKin)
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             self.numberKinetics = numKin      
#         else:
#             raise Exception(ERROR_CODE[error])
#                   
#     def SetKineticCycleTime(self, time):
#         error = self.dll.SetKineticCycleTime(c_float(time))
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             self.kineticCycleTime = time      
#         else:
#             raise Exception(ERROR_CODE[error])
# 
#     def SetImage(self, hbin, vbin, hstart, hend, vstart, vend):
#         error = self.dll.SetImage(hbin, vbin, hstart, hend, vstart, vend)
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             self.hstart = hstart
#             self.hend = hend
#             self.vstart = vstart
#             self.vend = vend
#             self.setDimensions((hend - hstart + 1), (vend - vstart + 1))
#             self.imageRegion = [hbin, vbin, hstart, hend, vstart, vend]
#         else:
#             raise Exception(ERROR_CODE[error])
# 
#     def StartAcquisition(self):
#         error = self.dll.StartAcquisition()
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             errorWait = self.dll.WaitForAcquisition()
#             if (ERROR_CODE[errorWait] == 'DRV_SUCCESS'):
#                 pass
#             else:
#                 raise Exception(ERROR_CODE[errorWait])                
#         else:
#             raise Exception(ERROR_CODE[error])
# 
#     def StartAcquisitionKinetic(self, numKin):
#         cnt = 0
#         error = self.dll.StartAcquisition()
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             # WaitForAcquisition finishes after ONE image is finished, this for loop will ensure
#             # that this method will wait for all images to be taken.
#             for i in range(numKin):
#                 errorWait = self.dll.WaitForAcquisition()
#                 if (ERROR_CODE[errorWait] != 'DRV_SUCCESS'):
#                     raise Exception(ERROR_CODE[errorWait])
#                 cnt += 1
#                 self.parent.onAcquisitionEvent("Acquired: {0} of {1}".format(cnt, numKin), self.parent.listeners)
#                 print "Acquired: {0} of {1}".format(cnt, numKin)                                
#         else:
#             raise Exception(ERROR_CODE[error])
#         
#     def StartAcquisitionKineticExternal(self):
#         error = self.dll.StartAcquisition()
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             pass
#         else:
#             raise Exception(ERROR_CODE[error])
# 
#     def WaitForAcquisition(self):
#         error = self.dll.WaitForAcquisition()
#         return ERROR_CODE[error]
#     
#     def GetAcquiredData(self):  
#         dim = self.width * self.height
#         cimageArray = c_int * dim
#         cimage = cimageArray()
#         #self.dll.WaitForAcquisition()
#         error = self.dll.GetAcquiredData(pointer(cimage),dim)
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             imageArray = cimage[:]
#             self.currentSingleImageArray = imageArray
#             self.singleImageArray.append(imageArray)
#             del imageArray
#         else:
#             raise Exception(ERROR_CODE[error])        
#     
#     def GetAcquiredDataKinetic(self, numKin):  
#         dim = self.width * self.height * numKin
#         cimageArray = c_int * dim
#         cimage = cimageArray()
#         #self.dll.WaitForAcquisition()
#         error = self.dll.GetAcquiredData(pointer(cimage),dim)
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             self.currentImageArray = cimage[:]
#             self.imageArray.append(cimage[:])
#             print 'acquired kinetic!'
#         else:
#             raise Exception(ERROR_CODE[error]) 
#    
#     def GetMostRecentImage(self):
#         #self.dll.WaitForAcquisition()
#         dim = self.width * self.height
#         cimageArray = c_int * dim
#         cimage = cimageArray()
#         error = self.dll.GetMostRecentImage(pointer(cimage),dim)
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             #self.imageArray = cimage[:]
#             return cimage[:]
#         else:
#             raise Exception(ERROR_CODE[error])
# 
#     def SetExposureTime(self, time):
#         error = self.dll.SetExposureTime(c_float(time))
#         if (ERROR_CODE[error] == 'DRV_SUCCESS'):
#             self.exposureTime = time        
#         else:
#             raise Exception(ERROR_CODE[error])
#         
#     def SetSingleScan(self):
#         self.SetReadMode(4)
#         self.SetAcquisitionMode(1)
#         self.SetImage(1,1,1,self.width,1,self.height)
# 
# 
#     def SaveAsTxt(self, path):
#                      
#         file = open(path, 'w')
#         
#         # self.imageArray is 1 dimensional!
#         count = 0
#         for i in self.imageArray:
#             file.write(str(int(i)))
#             count += 1
#             if (count == self.height):
#                 file.write("\n")
#                 count = 0
#             else:
#                 file.write(' ')
# 
#         file.close()
#         
#         #np.savetxt(path, np.reshape(self.imageArray, (self.height, self.width)))
#         
#     def SaveAsTxtKinetic(self, path, kinSet, numKin):
# #        # split up the image array into an array of arrays
# #        # ASSUMES CURRENT WIDTH AND HEIGHT ARE CORRECT FOR THE IMAGE!!!
# #        print 'from saveastxtkinetc numKin: ', numKin
# #        print 'from saveastxtkinetic len(imarray): ', len(self.imageArray)
# #        imageArray = np.reshape(self.imageArray, (numKin, 1, (len(self.imageArray)/numKin)))
# #        cnt = 0
# #        for image in np.arange(numKin):
# #            file = open(path + str(cnt), 'w')
# #            
# #            # self.imageArray is 1 dimensional!
# #            count = 0
# #            for i in imageArray[image][0]:
# #                file.write(str(int(i)))
# #                count += 1
# #                if (count == self.width):
# #                    file.write("\n")
# #                    count = 0
# #                else:
# #                    file.write(' ')
# #
# #            file.close()
# #            cnt += 1
#         
#          """ saving scheme: name-kinSet-numKin
#                         Ex: image-1-1
#                         Ex: image-1-27
#          """
#         
#          imageArray = np.reshape(self.currentImageArray, (numKin, self.height, self.width))
#          for image in np.arange(numKin):
#              np.savetxt(path+'-'+str(kinSet+1)+'-'+str(image+1), imageArray[image], fmt='%d')           
#             
#     def OpenAsTxt(self, path):
#         self.singleImageArray = np.ravel(np.loadtxt(path)) 
#         
#     def OpenAsTxtKinetic(self, path, kinSet, numKin):
#         """Assumes a series of txt files with a consecutive numbers appended to the end. Ex: image1, image2, image3..etc. 
#             
#             image12 means kinetic set 1, image 2
#             image122 means kinetic set 1, image 22
#             
#             The image array returned is 1 dimensional, with the images in sequential order. The images are sliced into rows.
#             
#             Ex: 2 sets of 3 images of size (2 rows, 3 cols)
#                 array of shape: (2, 3, 2, 3) -> (36)
#                 
#                 
#         
#             """
#         self.imageArray = []
#         imageArray = [[] for i in np.arange(numKin)]
#         for kinSetNumber in np.arange(kinSet):
#             for imageNumber in np.arange(numKin):
#                 imageArray[imageNumber] = np.loadtxt(path+'-'+str(kinSetNumber + 1)+'-'+str(imageNumber+1))
# #            imageArray = np.array(imageArray)
#             self.imageArray.append(np.ravel(np.array(imageArray))) #since labRAD doesn't like to transfer around multidimensional arrays (sorry!)
#         del imageArray
#         
#     @inlineCallbacks
#     def SaveToDataVault(self, directory, name):
#         dv = self.parent.client.data_vault
#         t1 = time.clock() 
#         width = np.arange(self.width + 1) + 1
#         height = np.arange(self.height + 1) + 1
# 
#         lenWidth = len(width)
#         lenHeight = len(height)
# 
#         Width = np.ravel([width]*lenHeight)
#         Height = []
#         for i in height:
#             Height.append([i]*lenWidth)
#         Height = np.ravel(np.array(Height))
#         
#         yield dv.cd(directory)
# #        yield self.cxn.data_vault.new('Half-Life', [('x', 'in')], [('y','','in')])         
# #        yield self.cxn.data_vault.add([[0.0,0.2],[1.0,0.2],[2.4,2.3],[3.3,0.0],[4.7,0.4],[4.5,1.2],[3.8,1.0],[2.3,4.8],[1.1,4.8],[1.1,4.1],[1.7,4.1],[2.0,3.4],[0.0,0.2]] )
# 
#         yield dv.new(name, [('Pixels', '')], [('Pixels','',''), ('Counts','','')])    
# 
#          
#         toDataVault = np.array(np.vstack((Height, Width, self.currentSingleImageArray)).transpose(), dtype=float)
#         yield dv.add(toDataVault)
#         t2 = time.clock()
#         print 'time for an image of size : ', (self.width + 1), (self.height + 1), (t2-t1), ' sec'
#         print 'saved!'        
# 
#     @inlineCallbacks
#     def SaveToDataVaultKinetic(self, directory, name, numKin):
#         dv = self.parent.client.data_vault
#         print len(self.currentImageArray)
#         print self.height
#         print self.width
#         print numKin
#         imageArray = np.reshape(self.currentImageArray, (numKin, 1, (self.height * self.width))) # needs to be currentImageArray!!!
#         for image in np.arange(numKin):
#             t1 = time.clock() 
#             print 'width: ', (self.width)
#             print 'height: ', (self.height)
#             width = np.arange(self.width) + 1
#             height = np.arange(self.height) + 1
#     
#             lenWidth = len(width)
#             lenHeight = len(height)
#     
#             Width = np.ravel([width]*lenHeight)
#             Height = []
#             for i in height:
#                 Height.append([i]*lenWidth)
#             Height = np.ravel(np.array(Height))
#             
#             yield dv.cd(directory, True)
#     #        yield self.cxn.data_vault.new('Half-Life', [('x', 'in')], [('y','','in')])         
#     #        yield self.cxn.data_vault.add([[0.0,0.2],[1.0,0.2],[2.4,2.3],[3.3,0.0],[4.7,0.4],[4.5,1.2],[3.8,1.0],[2.3,4.8],[1.1,4.8],[1.1,4.1],[1.7,4.1],[2.0,3.4],[0.0,0.2]] )
#             yield dv.new(name, [('Pixels', '')], [('Pixels','',''), ('Counts','','')])      
#             print 'Height: ', len(Height)
#             print 'Width: ', len(Width)
#             print 'shape: ', imageArray[image].shape   
#             yield dv.add_parameter('hstart', self.hstart)
#             yield dv.add_parameter('hend', self.hend)         
#             yield dv.add_parameter('vstart', self.vstart)
#             yield dv.add_parameter('vend', self.vend)
#             toDataVault = np.array(np.vstack((Height, Width, imageArray[image])).transpose(), dtype=float)
#             print toDataVault
#             yield dv.add(toDataVault)
#             t2 = time.clock()
#             print 'time for an image of size : ', (self.width + 1), (self.height + 1), (t2-t1), ' sec'
#             print 'saved!' 
#     
#     @inlineCallbacks
#     def OpenFromDataVault(self, directory, dataset):
#         dv = self.parent.client.data_vault
#         yield dv.cd(directory)
#         yield dv.open(dataset)
#         Data = yield dv.get()
#         data = Data.asarray
#         zData = np.array([None]*len(data))
#         for i in np.arange(len(data)):
#             zData[i] = data[i][2]
#             
#         self.singleImageArray = zData       
#         
#     
#     @inlineCallbacks
#     def OpenFromDataVaultKinetic(self, directory, numKin):
#         dv = self.parent.client.data_vault
#         yield dv.cd(directory)
#         for i in np.arange(numKin):
#             yield dv.open(int(i+1))
#             Data = yield dv.get()
#             data = Data.asarray
#             print data
#             print 'lendata: ', len(data)
#             zData = np.array([None]*len(data))
#             for j in np.arange(len(data)):
#                 zData[j] = data[j][2]
#                 
#             self.imageArray.append(zData)
#             print 'done!'            

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

    def shut_down(self):
        error = self.dll.ShutDown()
        print error
        return ERROR_CODE[error]
    
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

READ_MODE = {
    'Full Vertical Binning':0,
    'Multi-Track':1,
    'Random-Track':2,
    'Sinle-Track':3,
    'Image':4
                }

AcquisitionMode = {
    'Single Scan':1,
    'Accumulate':2,
    'Kinetics':3,
    'Fast Kinetics':4,
    'Run till abort':5
                   }

TriggerMode = {
    'Internal':0,
    'External':1,
    'External Start':6,
    'External Exposure':7,
    'External FVB EM':9,
    'Software Trigger':10,
    'External Charge Shifting':12
               }