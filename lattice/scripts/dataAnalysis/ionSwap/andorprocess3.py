import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import *
from matplotlib import pyplot
from scipy import ndimage
import peakdetect

initialDarkIonPositions = []
finalDarkIonPositions = []
ionMovements = []

typicalIonDiameter = 6 # compare sections of this size in the image
minimumIonIntensity = 530
maximumCorrectedIonIntensity = -150
expectedNumberOfIons = 5
peakVicinity = 3

choose = [6]

# loop through all the files
for s in choose:
    dataArray = []   
    for j in range(3):
        #j = 4
        try:
            #rawdata = np.loadtxt('/home/lattice/Downloads/andorimages/andorprocess/s' + str(j+1) + '.asc')
            rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-5ions-sample-dark\s' + str(s) + '000' + str(j+1) + '.asc')
            #rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-9ions-dark\s' + str(s) + '000' + str(j+1) + '.asc')
            rows, cols = rawdata.shape
            
            axialSumRegions = []
            axialData = np.sum(rawdata, 0)
            #meanRadialData = np.mean(radialData)
            
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
    
            # use this strip to create the 1-dimensional array of intensity sums
            procdata = rawdata[:, (maxIndex*typicalIonDiameter):(maxIndex*typicalIonDiameter + typicalIonDiameter)]
            data = np.array(rows)
            data = np.sum(procdata, 1) / typicalIonDiameter
            
            dataArray.append(data)
        
        except IOError:
            print 'failed to open something'
            
        ########### find the number of ions, peak positions of initial image ###########
        
    initialData_denoised = ndimage.gaussian_filter(dataArray[0], 3)
#        initialData_denoised = initialData_denoised[0:rows] # ?       
    initialMaxPeaks, initialMinPeaks = peakdetect.peakdetect(initialData_denoised, range(rows), 1, 1)
    initialPeakPositions = []
    for q in initialMaxPeaks:
        if q[1] > minimumIonIntensity:
            initialPeakPositions.append(q[0])
    
    if (len(initialPeakPositions) == expectedNumberOfIons):
        
        ########### find the number of ions, peak positions of initial dark image ###########
         
        initialDarkImageData = dataArray[1] - dataArray[0]
        initialDarkImageData_denoised = ndimage.gaussian_filter(initialDarkImageData, 3)
        initialDarkMaxPeaks, initialDarkMinPeaks = peakdetect.peakdetect(initialDarkImageData_denoised, range(rows), 1, 1)
        initialDarkPeakPositions = []
        for q in initialDarkMinPeaks:
            if q[1] < maximumCorrectedIonIntensity:
                initialDarkPeakPositions.append(q[0])
        
        if (len(initialDarkPeakPositions) == 1):
      
            ########### find the number of ions, peak positions of final dark image ###########
            
            finalDarkImageData = dataArray[2] - dataArray[0]
            finalDarkImageData_denoised = ndimage.gaussian_filter(finalDarkImageData, 3)
            finalDarkMaxPeaks, finalDarkMinPeaks = peakdetect.peakdetect(finalDarkImageData_denoised, range(rows), 1, 1)
            finalDarkPeakPositions = []
            for q in finalDarkMinPeaks:
                if q[1] < maximumCorrectedIonIntensity:
                    finalDarkPeakPositions.append(q[0])
           
            if (len(finalDarkPeakPositions) == len(initialDarkPeakPositions)):
                for q in initialPeakPositions:
                    if (abs(q - initialDarkPeakPositions[0]) < peakVicinity):
                        initialDarkIonPosition = np.where(initialPeakPositions == q)[0][0]
                        initialDarkIonPositions.append(initialDarkIonPosition)
                        break
                for q in initialPeakPositions:
                    if (abs(q - finalDarkPeakPositions[0]) < peakVicinity):
                        finalDarkIonPosition = np.where(initialPeakPositions == q)[0][0]
                        finalDarkIonPositions.append(finalDarkIonPosition)
                        break
                
                ionMovements.append(abs(finalDarkIonPosition - initialDarkIonPosition))
                                    
            else:
                print 'The incorrect number of ions are dark after recrystallization'
            
        else:
            print 'The incorrect number of ions went dark.'
    else:
        print 'An incorrect number of initial ions is present.'
     
        
    pyplot.plot(range(rows), initialData_denoised)
    pyplot.plot(range(rows), initialDarkImageData_denoised)
    pyplot.plot(range(rows), finalDarkImageData_denoised)
    
   
    print 'Initial Dark Ion Positions: ', initialDarkIonPositions
    print 'Final Dark Ion Positions: ', finalDarkIonPositions
    print 'Ion Movements: ', ionMovements

    
        
        
                            
            
#pyplot.figure(3)
#pyplot.plot(range(len(numberOfIons)), numberOfIons)
#pyplot.xlabel('Image Number')
#pyplot.ylabel('Number of Ions')

show()