from ctypes import *
import time
from PIL import Image
import sys
import numpy as np
import time
import peakdetect
from scipy import ndimage
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from labrad.server import LabradServer, setting, Signal
from AndorServer import Andor, AndorServer

class AndorIonCount(LabradServer, AndorServer):
    """ Contains methods that count ions in pictures taken by the Andor Luca"""
    
    name = "Andor Ion Count"

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
    
    def CountDarkIons(self, ionPositionCatalog, iterations, numKin):
        """ Returns the average number of dark ions in a sequence of images. 

           ionPositionCatalog is a list of lists of peak positions
            
            Ex:
                ionPositionCatalog[1st iteration] = [[peak positions background], [peak positions analyzed image], [peak positions analyzed image]]
                
                len(ionPositionCatalog[0][1]) = number of dark ions for the first image to be analyzed
                
        """
        
        numberImagesInSet = (numKin / iterations)
        
        darkIons = []
        
        for iteration in iterations:
            for image in np.arange(1,numberImagesInSet): # skip the background images
                darkIons.append(len(ionPositionCatalog[iteration][image]))
        
        totalNumberImagesAnalyzed = ((numKin / iterations) - 1) * iterations # = numKin - iterations # this excludes the 'initial' images
        return (np.sum(darkIons) / totalNumberImagesAnalyzed) 
    
    def CountIonSwaps(self, expectedNumberOfIons):
        pass
#        initialDarkIonPositions = []
#        for q in initialPeakPositions:
#            if (abs(q - initialDarkPeakPositions[0]) < peakVicinity):
#                initialDarkIonPosition = np.where(initialPeakPositions == q)[0][0]
#                initialDarkIonPositions.append(initialDarkIonPosition)
        """TODO: find the relative positions of the dark ions with the background, before and after, 
                 this assumes 2 images to be analyzed per background image
                 
                 save the imagearray as a textfile, process it so you can get separate files for
                 each image """
        
    def BuildIonPositionCatalog(self, peakPositionCatalog, iterations, numKin, expectedNumberOfIons, peakVicinity):
        """
        ionPositionCatalog is a list of lists of ion positions in the chain

        This catalog is built by assuming that each background image has the correct number of ions. The dark ion positions are
        determined by comparing the peak positions of the dark ions to the peak positions of the background image; if they fall within
        a certain 'peakVicinity,' then the dark ion is assigned the same position as one of the background ions.
        
        Ex:    (5 ions)
            
            peakPositionCatalog[1st iteration] = [[12, 26, 39, 53, 68], [24], [41]]
            ionPositionCatalog[1st iteration] = [[0, 1, 2, 3, 4], [1], [2]]
            
        Note: len(ionPositionCatalog[0][1]) = number of dark ions for the first image to be analyzed
        """

        ionPositionCatalog = [[] for i in range(iterations)] 

        numberImagesInSet = (numKin / iterations)

        for imageSet in np.arange(iterations):
            ionPositionCatalog[imageSet][0] = np.arange(len(peakPositionCatalog[imageSet][0])) #background image
            for image in np.arange(1, numberImagesInSet):
               
                for peakPosition in peakPositionCatalog[imageSet][image]:
                    result = np.where(abs(np.subtract(peakPositionCatalog[imageSet][0], peakPosition)) <= peakVicinity)[0]
                    # assumes that one dark ion will never be close enough to multiple initial ion position
                    if (len(result) != 0):
                        ionPositionCatalog[imageSet][image] = result[0]
        
        return ionPositionCatalog
                
    
    def GetPeakPositionCatalog(self, numKin, rows, cols, typicalIonDiameter, initialThreshold, darkThreshold, iterations):
        """This method counts the number of dark ions (and their positions) in 
            an ion chain. It is required that the background image contain a 
            fully illuminated chain of ions.
        
            numkin - total number of images in the data array.    
           
           This method assumes that for each background image taken, there is
           ((numKin / iterations) - 1) images for comparison.
           
           Example: numKin = 50, iterations = 10
                    for each background image, the following 4 images will be
                    analyzed against it.
                    
                    (1 + 4) * 10 = 50
                    
                    1 background, 4 images.
                    
                    Therefore: 10 'sets' of 5 images.
                    
            NOTE: Assumes collectData was just run!
                    
        """
        
        numberImagesInSet = (numKin / iterations)
        numberImagesToAnalyze = (numKin / iterations) - 1
        
        # 3D array of each image
        data = np.reshape(np.array(self.camera.imageArray), (numKin, rows, cols))
        
        peakPositionCatalog = [[] for i in range(iterations)] 
        
        """ peakPositionCatalog is a list of lists of peak positions
            
            Ex:
                peakPositionCatalog[1st iteration] = [[peak positions background], [peak positions analyzed image], [peak positions analyzed image]]
                
                len(peakPositionCatalog[0][1]) = number of dark ions for the first image to be analyzed
            
        """
        
        for imageSet in np.arange(iterations):
            sumArray = []
            for image in np.arange(numberImagesInSet):
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
                axialData = np.sum(data[numberImagesInSet*imageSet + image], 1) # 1D vector: sum of intensities in the axial direction. length = rows
                
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
                        
                # find the index strip with the highest intensity
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
                mostIntenseData = data[numberImagesInSet*set + image][(mostIntenseRegionIndex*typicalIonDiameter):(mostIntenseRegionIndex*typicalIonDiameter + typicalIonDiameter), :]
                mostIntenseDataSums = np.sum(mostIntenseData, 0) / typicalIonDiameter #1D vector
                
                sumArray.append(mostIntenseDataSums)
            
            ########### find the number of ions, peak positions of initial image ########### 
            initialDenoised = ndimage.gaussian_filter(sumArray[0], 2)    
            initialMaxPeaks, initialMinPeaks = peakdetect.peakdetect(initialDenoised, range(cols), 1, 1)
            initialPeakPositions = []
            for peak in initialMaxPeaks: # peak = [position (pixel), intensity]
                if peak[1] > initialThreshold:
                    initialPeakPositions.append(peak[0])
            print 'initial peak positions: ', initialPeakPositions
            
            peakPositionCatalog[set].append(initialPeakPositions)
            
            ########### find the number of dark ions, peak positions of analyzed images ###########
            for image in np.arange(numberImagesToAnalyze):
                subtractedData = sumArray[(image+1)] - sumArray[0]
                subtractedDataDenoised = ndimage.gaussian_filter(subtractedData, 2)
                darkMaxPeaks, darkMinPeaks = peakdetect.peakdetect(subtractedDataDenoised, range(cols), 1, 1)
                darkPeakPositions = []
                for peak in darkMinPeaks:
                    if peak[1] < darkThreshold:
                        darkPeakPositions.append(peak[0])
                print 'initial dark peak positions: ', darkPeakPositions
                peakPositionCatalog[set].append(darkPeakPositions) # we're hoping there is only one peak here!
        
           
        return peakPositionCatalog    
            
            
    @setting(40, "Collect Data", height = 'i', width = 'i', iterations = 'i', returns = 'i')
    def collectData(self, c, height, width, iterations):
        """Given the iterations, will return the average number of ions"""
        self.camera.GetStatus()
        status = self.camera.status
        if (status == 'DRV_IDLE'):
            numKin = 2*iterations
            self.camera.SetAcquisitionMode(3)
            self.camera.SetNumberKinetics(numKin)
            self.camera.SetKineticCycleTime(0.02)
            print 'Starting Acquisition (Ion Count)'
            yield deferToThread(self.camera.StartAcquisitionKinetic, numKin)
            yield self.camera.GetAcquiredDataKinetic(numKin)
                                    
        else:
            raise Exception(status)
        
    @setting(41, "Count Dark Ions", numKin = 'i', rows = 'i', cols = 'i', typicalIonDiameter = 'i', initialThreshold = 'i', darkThreshold = 'i', iterations = 'i', returns = 'v')
    def countDarkIons(self, c, numKin, rows, cols, typicalIonDiameter, expectedNumberOfIons, initialThreshold, darkThreshold, iterations):
        peakPositionCatalog = self.GetPeakPositionCatalog(numKin, rows, cols, typicalIonDiameter, expectedNumberOfIons, initialThreshold, darkThreshold, iterations)
        avgNumberDarkIons = self.CountDarkIons(peakPositionCatalog, iterations, numKin)
        returnValue(avgNumberDarkIons)
    
    @setting(42, "Count Ion Swaps", numKin = 'i', rows = 'i', cols = 'i', typicalIonDiameter = 'i', initialThreshold = 'i', darkThreshold = 'i', iterations = 'i', expectedNumberOfIons = 'i', peakVicinity = 'i', returns = 'i')
    def countIonSwaps(self, c, numKin, rows, cols, typicalIonDiameter, expectedNumberOfIons, initialThreshold, darkThreshold, iterations, expectedNumberOfIons, peakVicinity):
        peakPositionCatalog = self.GetPeakPositionCatalog(numKin, rows, cols, typicalIonDiameter, initialThreshold, darkThreshold, iterations)
        ionPositionCatalog = self.BuildIonPositionCatalog(peakPositionCatalog)

        
if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorIonCount())