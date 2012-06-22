import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import *
from matplotlib import pyplot
from scipy import ndimage
import peakdetect
import time

iterations = 1

#initialDarkIonPositionsHistory = []
#finalDarkIonPositionsHistory = []
ionMovements = []

typicalIonDiameter = 6 # compare sections of this size in the image
minimumIonIntensity = 540
maximumCorrectedIonIntensity = -50
expectedNumberOfIons = 3
peakVicinity = 3

imagesWithIncorrectInitialIonNumber = 0
imagesWithIncorrectInitialDarkIonNumber = 0
imagesWithIncorrectFinalDarkIonNumber = 0


timeOpening = 0
timeProcessing = 0

# loop through all the files
for s in range(iterations):
    dataArray = []
    initialData_denoised = []
    uncorrectedInitialDarkImageData_denoised = []
    uncorrectedFinalDarkImageData_denoised = []
    initialDarkImageData_denoised = []
    finalDarkImageData_denoised = []

    print 'Iteration: ', s+1
    try:
        for j in np.arange(1,4):
            #j = 4
                #rawdata = np.loadtxt('/home/lattice/Downloads/andorimages/andorprocess/s' + str(j+1) + '.asc')
                #rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-5ions-sample-dark\s6000' + str(3*s + j) + '.asc')
                #rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-9ions-dark\s' + str(s) + '000' + str(j+1) + '.asc')
                #rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\camera-test\s100' + str(3*s + j) + '.asc')
                t1 = time.clock()
                try:
                   rawdata = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062112\4\processed\s100' + str(3*s + j) + '.asc')
                except IOError: #only 9 of these
                   rawdata = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062112\4\processed\s1000' + str(3*s + j) + '.asc')
                rows, cols = rawdata.shape
                t2 = time.clock()
                timeOpening += (t2-t1)
                
                matshow(rawdata)
                axialSumRegions = []
                axialData = np.sum(rawdata, 0)
                
                # find the sum of the intensities of each strip
                intensitySum = 0
                cnt = 0
                for i in np.arange(cols):
                    intensitySum = intensitySum = axialData[i]
                    cnt = cnt + 1
                    if (cnt == typicalIonDiameter):
                        axialSumRegions.append(intensitySum)
                        cnt = 0
                        intensitySum = 0
                      
                # find the strip with the highest intensity
                temp = 0
                for i in np.arange(len(axialSumRegions)):
                    if axialSumRegions[i] > temp:
                        temp = axialSumRegions[i]
                        maxIndex = i
                print 'Image ' + str(j) + ' - Region picked with highest intensity: ', maxIndex        
        
                # use this strip to create the 1-dimensional array of intensity sums
                procdata = rawdata[:, (maxIndex*typicalIonDiameter):(maxIndex*typicalIonDiameter + typicalIonDiameter)]
                data = np.array(rows)
                data = np.sum(procdata, 1) / typicalIonDiameter
                
                dataArray.append(data)
                            
            ########### find the number of ions, peak positions of initial image ###########
            
        initialData_denoised = ndimage.gaussian_filter(dataArray[0], 2)
    #        initialData_denoised = initialData_denoised[0:rows] # ?       
        initialMaxPeaks, initialMinPeaks = peakdetect.peakdetect(initialData_denoised, range(rows), 1, 1)
        initialPeakPositions = []
        for q in initialMaxPeaks:
            if q[1] > minimumIonIntensity:
                initialPeakPositions.append(q[0])
        print 'initial peak positions: ', initialPeakPositions
        
        if (len(initialPeakPositions) != expectedNumberOfIons):
            
            ########### find the number of ions, peak positions of initial dark image ###########
             
            t3 = time.clock()
            initialDarkImageData = dataArray[1] - dataArray[0]
            uncorrectedInitialDarkImageData_denoised = ndimage.gaussian_filter(dataArray[1], 2)
            initialDarkImageData_denoised = ndimage.gaussian_filter(initialDarkImageData, 2)
            initialDarkMaxPeaks, initialDarkMinPeaks = peakdetect.peakdetect(initialDarkImageData_denoised, range(rows), 1, 1)
            initialDarkPeakPositions = []
            for q in initialDarkMinPeaks:
                if q[1] < maximumCorrectedIonIntensity:
                    initialDarkPeakPositions.append(q[0])
            print 'initial dark peak positions: ', initialDarkPeakPositions
            t4 = time.clock()
            timeProcessing += (t4-t3)
            
            if (len(initialDarkPeakPositions) == 1):
          
                ########### find the number of ions, peak positions of final dark image ###########
                
                finalDarkImageData = dataArray[2] - dataArray[0]
                uncorrectedFinalDarkImageData_denoised = ndimage.gaussian_filter(dataArray[2], 2)
                finalDarkImageData_denoised = ndimage.gaussian_filter(finalDarkImageData, 2)
                finalDarkMaxPeaks, finalDarkMinPeaks = peakdetect.peakdetect(finalDarkImageData_denoised, range(rows), 1, 1)
                finalDarkPeakPositions = []
                for q in finalDarkMinPeaks:
                    if q[1] < maximumCorrectedIonIntensity:
                        finalDarkPeakPositions.append(q[0])
                print 'final dark peak positions: ', finalDarkPeakPositions
               
                if (len(finalDarkPeakPositions) == len(initialDarkPeakPositions)):
                    initialDarkIonPositions = []
                    for q in initialPeakPositions:
                        if (abs(q - initialDarkPeakPositions[0]) < peakVicinity):
                            initialDarkIonPosition = np.where(initialPeakPositions == q)[0][0]
                            initialDarkIonPositions.append(initialDarkIonPosition)
            #                            initialDarkIonPositionsHistory.append(initialDarkIonPosition)
                    print 'initial dark ion positions: ', initialDarkIonPositions
                            #break
                    finalDarkIonPositions = []
                    for q in initialPeakPositions:
                        if (abs(q - finalDarkPeakPositions[0]) < peakVicinity):
                            finalDarkIonPosition = np.where(initialPeakPositions == q)[0][0]
                            finalDarkIonPositions.append(finalDarkIonPosition)
            #                            finalDarkIonPositionsHistory.append(finalDarkIonPosition)
                            #break
                    print 'final dark ion positions: ', finalDarkIonPositions
                    
                    ionMovements.append(abs(finalDarkIonPosition - initialDarkIonPosition))
                                        
                else:
                    print 'The incorrect number of ions are dark after recrystallization'
                    imagesWithIncorrectFinalDarkIonNumber += 1
            else:
                print 'The incorrect number of ions went dark.'
                imagesWithIncorrectInitialDarkIonNumber += 1
        else:
            print 'An incorrect number of initial ions is present.'
            print len(initialPeakPositions)
            imagesWithIncorrectInitialIonNumber += 1

    except IOError:
        print 'failed to open something'
         
    try:
        pyplot.figure()
        xaxis = range(rows)
        pyplot.plot(xaxis, initialData_denoised, label='initial')
        pyplot.plot(xaxis, uncorrectedInitialDarkImageData_denoised, label='uncorrected-dark')
        pyplot.plot(xaxis, uncorrectedFinalDarkImageData_denoised, label='uncorrected-rextal')
        pyplot.plot(xaxis, initialDarkImageData_denoised, label='corrected-dark')
        pyplot.plot(xaxis, finalDarkImageData_denoised, label='corrected-rextal')
        pyplot.legend(loc='best')
    except:
        print 'whatever'
      
ionMovements = np.array(ionMovements)
print 'Number of Swaps: ', len(np.where(ionMovements == 1)[0])

            
#pyplot.figure(3)
#pyplot.plot(range(len(numberOfIons)), numberOfIons)
#pyplot.xlabel('Image Number')
#pyplot.ylabel('Number of Ions')
print timeOpening
print timeProcessing

show()