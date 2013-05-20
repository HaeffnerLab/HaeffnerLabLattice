import numpy as np
import matplotlib

from pylab import *
from matplotlib import pyplot
from scipy import ndimage
import peakdetect





def GetPeakPositionCatalog(numSet, numKin, rows, cols, typicalIonDiameter, initialThreshold, darkThreshold, iterations):
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
    
    numSet += 6
    
    numberImagesInSet = (numKin / iterations)
    numberImagesToAnalyze = (numKin / iterations) - 1
    
    
    # 3D array of each image
#    try:
#        data = np.reshape(np.array(self.camera.imageArray), (numKin, rows, cols))
#    except ValueError:
#        raise Exception("Trying to analyze more images than there is in the data? Image region correct?")
#        data = self.imageArray
    
#        ###### TESTING TESTING TESTING 123 ################
#    rawdata1 = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062812\7\image19')
    
#        
#    rawdata2 = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062812\7\image20')
#
#    rawdata3 = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062812\7\image21')
#        

#        # ion swap
    arr = [[] for i in range(3)]
    for j in range(3):
        arr[j] = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062812\7\image-1-' + str(3*numSet + j + 1))
#        arr[3] = rawdata1
#        arr[4] = rawdata1
#        arr[5] = rawdata3
#                        
    data = np.array(arr)
#        
#        ###### TESTING TESTING TESTING 123 ################
    
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


            mostIntenseData = data[numberImagesInSet*imageSet + image][(mostIntenseRegionIndex*typicalIonDiameter):(mostIntenseRegionIndex*typicalIonDiameter + typicalIonDiameter), :]
            mostIntenseDataSums = np.sum(mostIntenseData, 0) / typicalIonDiameter #1D vector
            
            """
                      |      |      |      |      |
                _____/|\____/|\____/|\____/|\____/|\_____   background image sum
                
                
                ___________________   ___________________   dark ion image sum (background subtracted out)
                                   \|/
                                    |
            
            """
            
            sumArray.append(mostIntenseDataSums)

        ########### find the number of ions, peak positions of initial image ########### 
        initialDenoised = ndimage.gaussian_filter(sumArray[0], 2)

        initialMaxPeaks, initialMinPeaks = peakdetect.peakdetect(initialDenoised, range(cols), 1, 1)
        initialPeakPositions = []
        for peak in initialMaxPeaks: # peak = [position (pixel), intensity]
            if peak[1] > initialThreshold:
                initialPeakPositions.append(peak[0])
#            print 'initial peak positions: ', initialPeakPositions
#            print 'number of ions: ', len(initialPeakPositions)

        pyplot.figure()
        xaxis = range(cols)
        pyplot.plot(xaxis, initialDenoised, label=('initial' + ' ' + str(numSet + 1)))
        
        peakPositionCatalog[imageSet].append(initialPeakPositions)
        
        ########### find the number of dark ions, peak positions of analyzed images ###########
        for image in np.arange(numberImagesToAnalyze):
            subtractedData = sumArray[(image+1)] - sumArray[0]
            subtractedDataDenoised = ndimage.gaussian_filter(subtractedData, 2)
            darkMaxPeaks, darkMinPeaks = peakdetect.peakdetect(subtractedDataDenoised, range(cols), 1, 1)
            darkPeakPositions = []
            for peak in darkMinPeaks:
                if peak[1] < darkThreshold:
                    darkPeakPositions.append(peak[0])

#                print 'initial dark peak positions: ', darkPeakPositions
#                print 'number of dark ions: ', len(darkPeakPositions)
            peakPositionCatalog[imageSet].append(darkPeakPositions) # we're hoping there is only one peak here!
            pyplot.plot(xaxis, subtractedDataDenoised, label=('dark'+str(image) + ' ' + str(numSet + 1)))
            
        pyplot.legend(loc='best')

        

###############-------------------------------######################

iterations = 1
typicalIonDiameter = 5 # compare sections of this size in the image
initialThreshold = 700
darkThreshold = -350
expectedNumberOfIons = 9
peakVicinity = 3
hstart = 455
hend = 530
vstart = 217
vend = 242
numKin = 3

rows = vend - vstart + 1
cols = hend - hstart + 1

for numSet in range(1):
    GetPeakPositionCatalog(numSet, numKin, rows, cols, typicalIonDiameter, initialThreshold, darkThreshold, iterations)

           
#        print 'peak positionn catalog:'
#        print peakPositionCatalog
#pyplot.figure()
#xaxis = range(rows)
#pyplot.plot(xaxis, initialData_denoised, label='initial')
#pyplot.plot(xaxis, uncorrectedInitialDarkImageData_denoised, label='uncorrected-dark')
#pyplot.plot(xaxis, uncorrectedFinalDarkImageData_denoised, label='uncorrected-rextal')
#pyplot.plot(xaxis, initialDarkImageData_denoised, label='corrected-dark')
#pyplot.plot(xaxis, finalDarkImageData_denoised, label='corrected-rextal')
#pyplot.legend(loc='best')


      
            
#pyplot.figure(3)
#pyplot.plot(range(len(numberOfIons)), numberOfIons)
#pyplot.xlabel('Image Number')
#pyplot.ylabel('Number of Ions')

show()