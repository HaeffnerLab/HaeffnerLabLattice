from ctypes import *
import time
from PIL import Image
import sys
import numpy as np
import time
import peakdetect
from scipy import ndimage
from matplotlib import pyplot
from scipy import optimize
from scipy.stats import chisquare
from itertools import product
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from labrad.server import LabradServer, setting, Signal
from AndorServer import Andor, AndorServer

"""
    this pulse sequence has one reference image taken via internal trigger and has 2*iterations images per kinetic set (one initial and final). An overall odd number of images
    Assumed for ion swap experiment. total: numKineticSets*(reference + itereations*(initial + final) 
    
"""


class AndorIonCount(LabradServer, AndorServer):
    """ Contains methods that count ions in pictures taken by the Andor Luca"""
    
    name = "Andor Ion Count"

    def initServer(self):

        self.listeners = set()  
        self.prepareCamera()
        self.positionDict = {
                            '2':                                  [-.62996, .62996],
                            '3':                                 [-1.0772, 0, 1.0772],
                            '4':                          [-1.4368, -.45438, .45438, 1.4368],
                            '5':                         [-1.7429, -0.8221, 0, 0.8221, 1.7429],
                            '6':                  [-2.0123, -1.4129, -.36992, .36992, 1.4129, 2.0123],
                            '7':                 [-2.2545, -1.1429, -.68694, 0, .68694, 1.1429, 2.2545],
                            '8':           [-2.4758, -1.6621, -.96701, -.31802, .31802, .96701, 1.6621, 2.4758],
                            '9':         [-2.6803, -1.8897, -1.2195, -.59958, 0, .59958, 1.2195, 1.8897, 2.6803],
                            '10': [-2.8708, -2.10003, -1.4504, -.85378, -.2821, .2821, .85378, 1.4504, 2.10003, 2.8708]
                            }        

    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified
    
       
    def _getIonNumberCatalog(self, image, darkIonPositionCatalog, iterations, kinSet, numKin):
        """image = 1 or 2
        
           Note: the array is in order of kinetic set and iteration
        """
        
        numberKineticSets = kinSet
        
        ionNumberCatalog = []
        
        for kinSet in np.arange(numberKineticSets):
            for iteration in np.arange(iterations):
                ionNumberCatalog.append(len(darkIonPositionCatalog[kinSet][iteration][image - 1]))
        
        return ionNumberCatalog
           
    
    def _buildIonSwapCatalog(self, darkIonPositionCatalog, kinSet, iterations, expectedNumberOfIons):
        """  returns a 1D array describing the distance an ion travelled by comparing the initial
             and final images.
         
             this assumes 2 images to be analyzed per background image. Also assumes that there is 
             only ONE dark ion in both images.
             
             Note: the array is in order of kinetic set
             
         """
        
       
        numberKineticSets = kinSet
        ionSwapCatalog = []
        
        for kinSet in np.arange(numberKineticSets):
            for imageSet in np.arange(iterations):
                if (len(darkIonPositionCatalog[kinSet][imageSet][0]) == 1):
                    initialPosition = darkIonPositionCatalog[kinSet][imageSet][0]
                    if (len(darkIonPositionCatalog[kinSet][imageSet][1]) == 1):
                        finalPosition = darkIonPositionCatalog[kinSet][imageSet][1]                  
                        ionSwapCatalog.append(abs(finalPosition - initialPosition))
                
                print 'number dark ions in first image: ', len(darkIonPositionCatalog[kinSet][imageSet][0])
                print 'number dark ions in second image: ', len(darkIonPositionCatalog[kinSet][imageSet][1])

#        print 'ion swap catalog:'
#        print ionSwapCatalog
        print 'len of ion swap catalog: ', len(ionSwapCatalog)
        return ionSwapCatalog
    



    def _fit(self, function, parameters, expectedNumberOfIons, y, x = None):  
        solutions = [None]*len(parameters)
        def f(params):
            i = 0
            for p in params:
                solutions[i] = p
                i += 1
            return (y - function(x, params, expectedNumberOfIons))
        if x is None: x = np.arange(y.shape[0])
        optimize.leastsq(f, parameters)
        return solutions
    
    def _fitFunction(self, x, p, expectedNumberOfIons):
        """p = [height, alpha, axialOffset, sigma, offset] """   
        fitFunc = 0
        for i in self.positionDict[str(expectedNumberOfIons)]:
            fitFunc += p[0]*np.exp(-(((x-i*p[1] - p[2])/p[3])**2)/2)
    #    fitFunc = offset() + height()*exp(-(((x+1.7429*alpha())/sigma())**2)/2) + height()*exp(-(((x+0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x)/sigma())**2)/2) + height()*exp(-(((x-0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x-1.7429*alpha())/sigma())**2)/2)
        return fitFunc + p[4]
    
    def _getOneDDdata(self, data, rows, cols, typicalIonDiameter):
        """ The image, assumed to be have more columns than rows, will first be analyzed
            in the axial direction. The sums of the intensities will be collected in the
            axial direction first. This will help narrow down which section of the image,
            in order to exclude noise.
            
            Example:   |  [[ # # # # # # # # # # # # # # # # # # # # # #],       |
                       0   [ # # # # # # # # # # # # # # # # # # # # # #], avgIonDiameter
                       |   [ # # # # # # # # # # # # # # # # # # # # # #],       |
                      |    [ * * * * * * * * * * * * * * * * * * * * * *], <-- strip of highest intensity,
                      1    [ * * * * * * * * * * * * * * * * * * * * * *], <-- will only be used for 
                      |    [ * * * * * * * * * * * * * * * * * * * * * *], <-- proceeding calculations
                       |   [ % % % % % % % % % % % % % % % % % % % % % %],
                       2   [ % % % % % % % % % % % % % % % % % % % % % %],
                       |   [ % % % % % % % % % % % % % % % % % % % % % %]]
                                  
                                             Axial   
        """
        
        
        axialSumSegments = []
        axialData = np.sum(data, 1) # 1D vector: sum of intensities in the axial direction. length = rows

        
        """ choose each strip by only analyzing the 1D vector of sums
            
            [ # # # * * * % % %] -> [# * %]
                                     0 1 2
                      ^                ^
                      |                |
                    Segment           most
                                    intense
                                      sum
        """
        intensitySum = 0
        cnt = 0
        for i in np.arange(rows):
            intensitySum += axialData[i]
            cnt += 1
            if (cnt == typicalIonDiameter):
                axialSumSegments.append(intensitySum)
                cnt = 0
                intensitySum = 0 
                
        # find the index of the strip with the highest intensity
        mostIntenseRegionIndex = np.where(axialSumSegments == np.max(axialSumSegments))[0][0]
        
        """ use this strip to create the 1-dimensional array of intensity sums in the radial direction
        
            [ * * * * * * * * * * * * * * * * * * * * * *] 1D vector of sums
                                                            in the radial direction
                                  ^                            length = cols
                                  |                        Used to find peaks
           
           [[ * * * * * * * * * * * * * * * * * * * * * *], most 
            [ * * * * * * * * * * * * * * * * * * * * * *], intense
            [ * * * * * * * * * * * * * * * * * * * * * *]]  strip
            
            
        
        """


        mostIntenseData = data[(mostIntenseRegionIndex*typicalIonDiameter):(mostIntenseRegionIndex*typicalIonDiameter + typicalIonDiameter), :]
        mostIntenseDataSums = np.sum(mostIntenseData, 0) / typicalIonDiameter #1D vector
        
        return mostIntenseDataSums
        
    
    def _fitInitialImage(self, kinSet, rows, cols, typicalIonDiameter, expectedNumberOfIons, initialParameters):
        
        """initialParameters = [alpha, axialOffset, sigma]
        
                            the offset and height are already approximated by the data"""
        parametersArray = []
        
        initialImageArray = self.camera.GetAcquiredData()
        data = np.reshape(initialImageArray, (kinSet, rows, cols))        
        
        for kineticSet in np.arange(kinSet):
            axialSums = self._getOneDDdata(data[kineticSet], rows, cols, typicalIonDiameter)
            
            
            # start here
#            xmodel = np.arange(len(axialSums), dtype=float)
        
 
            alpha = initialParameters[0] #Parameter(15)
            axialOffset = initialParameters[1] #Parameter(33)
            offset = Parameter(np.min(axialSums))
            height = Parameter(np.max(axialSums) - np.min(axialSums))
            sigma = initialParameters[2]        
        
            alpha, axialOffset, offset, height, sigma = self._fit(self._fitFunction, [height, alpha, axialOffset, sigma, offset], expectedNumberOfIons, axialSums)
            print 'alpha: ', alpha
            print 'axialOffset: ', axialOffset
            print 'offset: ', offset
            print 'height: ', height
            print 'sigma: ', sigma
            
#            ymodel = self._fitFunction(xmodel, [alpha, axialOffset, offset, height, sigma], expectedNumberOfIons)
            
#            pyplot.plot(xmodel, axialSums)
#            pyplot.plot(xmodel, ymodel)
            parametersArray.append([alpha, axialOffset, offset, height, sigma])
        return parametersArray       
    
    def _BuildDarkIonPositionCatalog(self, parametersArray, kinSet, numKin, rows, cols, typicalIonDiameter, expectedNumberOfIons, iterations):
        
        """parametersArray[1st kinetic set] = [height, alpha, axialOffset, sigma, offset]
       
        darkIonPositionCatalog is a list of lists of ion positions in the chain


        
        Ex:    (5 ions)
            
            darkIonPositionCatalog[1st kinetic set][1st iteration][1st image] =    [1, 2] --> means two dark ions at positions 1 and 2 in the ion chain
            
                                                                                    ^
                                                                                    | --> dark ion position in [0, 1, 2, 3, 4]
                                                                            
            
        Note: len(darkIonPositionCatalog[0][1]) = number of dark ions for the first image to be analyzed
        
        """        
        
        try:
            data = np.reshape(np.array(self.camera.imageArray), (kinSet, numKin, rows, cols))
        except ValueError:
            raise Exception("Trying to analyze more images than there is in the data? Image region correct?")

        numberImagesInSet = (numKin / iterations) # better equal 2 for ionSwap

        darkIonPositionCatalog = [[[] for i in range(iterations)] for j in range(kinSet)]

        xmodel = np.arange(cols, dtype=float)
        
        for kineticSet in np.arange(kinSet):
            for imageSet in np.arange(iterations):
                for image in np.arange(numberImagesInSet):
                    axialSums = self._getOneDDdata(data[kineticSet][numberImagesInSet*imageSet + image], rows, cols, typicalIonDiameter) 
                    
                    
                    t1 = time.clock()
                    bestFitIonArrangement = [] # 1 = bright, 0 = dark, Ex: (1, 1, 0, 1, 1)
                    bestChiSquare = float(10000000) # get rid of this in the future and make the if statement a try/except
                    positionValues = self.positionDict[str(expectedNumberOfIons)]
                    for ionArrangement in product(range(2), repeat=expectedNumberOfIons):
                        # build the model function, expected to have at least one component = 0 (have an ion dark in the model function)
                        darkModel = 0
                        for ion in np.arange(expectedNumberOfIons):
                            if ionArrangement[ion] == 1:
                                print ionArrangement, ion
                                print positionValues[ion]
                                darkModel += parametersArray[kineticSet][0]*np.exp(-(((xmodel-positionValues[ion]*parametersArray[kineticSet][1] - parametersArray[kineticSet][2])/parametersArray[kineticSet][3])**2)/2)
                        
                        darkModel += parametersArray[kineticSet][4]
                        
                        try:
                            tempChiSquare, pValue = chisquare(axialSums, darkModel)
                            if (tempChiSquare < bestChiSquare):
                                bestChiSquare = tempChiSquare
                                bestFitIonArrangement = ionArrangement
                        except AttributeError:
                            print 'loca!'
                    t2 = time.clock()
                    print 'time: ', (t2-t1)
                    print 'best: ', bestChiSquare, bestFitIonArrangement
                    darkIonPositions = np.where(bestFitIonArrangement == 0)[0] # awesome
                    print darkIonPositions
                    darkIonPositionCatalog[kineticSet][imageSet].append(darkIonPositions)
        
        return darkIonPositionCatalog        
              
            
    @setting(40, "Collect Data", height = 'i', width = 'i', iterations = 'i', numAnalyzedImages = 'i', returns = '')
    def collectData(self, c, height, width, iterations, numAnalyzedImages):
        """Given the iterations, will return the average number of ions"""
        self.camera.GetStatus()
        status = self.camera.status
        if (status == 'DRV_IDLE'):
            numKin = (numAnalyzedImages + 1)*iterations # Number of images in kinetic series = numAnalyzedImages + the background image 
            self.camera.SetAcquisitionMode(3)
            self.camera.SetNumberKinetics(numKin)
#            self.camera.SetKineticCycleTime(0.01)
            print 'Starting Acquisition (Ion Count)'
            yield deferToThread(self.camera.StartAcquisitionKineticExternal)
#            yield self.camera.GetAcquiredDataKinetic(numKin)
            print 'Started!'
                                    
        else:
            raise Exception(status)
                                
    @setting(43, "Get Ion Number Histogram", image = 'i', kinSet = 'i', numKin = 'i', rows = 'i', cols = 'i', iterations = 'i', returns = '*i')
    def getIonNumberHistogram(self, c, image, kinSet, numKin, rows, cols, iterations):        
        """For Ion Swap, image should = 1, 2 or 3 """
        ionNumberCatalog = self._getIonNumberCatalog(image, self.darkIonPositionCatalog, iterations, kinSet, numKin)
        if (len(ionNumberCatalog) != 0):
            return ionNumberCatalog
        else:
            raise Exception("There are no ions!")
        
    @setting(44, "Get Ion Swap Histogram", iterations = 'i', kinSet = 'i', numKin = 'i', expectedNumberOfIons = 'i', returns = '*i')
    def getIonSwapHistogram(self, c, iterations, kinSet, numKin, expectedNumberOfIons):
        ionSwapCatalog = self._buildIonSwapCatalog(self.darkIonPositionCatalog, kinSet, iterations, expectedNumberOfIons)
        if (len(ionSwapCatalog) != 0):
            return np.array(ionSwapCatalog)
        else:
            raise Exception("There are no ions!")     
        
    @setting(45, "Build Dark Ion Position Catalog", kinSet = 'i', numKin = 'i', rows = 'i', cols = 'i', typicalIonDiameter = 'i', expectedNumberOfIons = 'i', iterations = 'i', initialParameters = '*i', returns = '')
    def buildDarkIonPositionCatalog(self, c, kinSet, numKin, rows, cols, typicalIonDiameter, expectedNumberOfIons, iterations, initialParameters):
        parametersArray = self._fitInitialImage(kinSet, rows, cols, typicalIonDiameter, expectedNumberOfIons, initialParameters)
        self.darkIonPositionCatalog = self._BuildDarkIonPositionCatalog(parametersArray, kinSet, numKin, rows, cols, typicalIonDiameter, expectedNumberOfIons, iterations)
        print self.darkIonPositionCatalog

        
if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorIonCount())