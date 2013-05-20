import numpy as np
import matplotlib

from pylab import *
from matplotlib import pyplot
from scipy import ndimage
import peakdetect

numberOfIons = []
ionDistances = []

typicalIonDiameter = 6 # compare sections of this size in the image
minimumIonIntensity = 505

choose = [1]

# loop through all the files
for s in choose:
    for j in range(9):
        #j = 4
        try:   
            #rawdata = np.loadtxt('/home/lattice/Downloads/andorimages/andorprocess/s' + str(j+1) + '.asc')
            #rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-5ions-sample-dark\s' + str(s) + '000' + str(j+1) + '.asc')
            #rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-9ions-dark\s' + str(s) + '000' + str(j+1) + '.asc')
            rawdata = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\060612\1\processed\1\s' + str(s) + '000' + str(j+1) + '.asc')
            rows, cols = rawdata.shape
            
            print rows
            
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
            
            #print data[:]/means[:]
            pyplot.figure(1)
            pyplot.plot(range(rows), data, label=str(j+1))
            pyplot.xlabel('Axial Direction (pixels)')
            pyplot.ylabel('Average Intensity (counts/sec)')
            
            # find the number of ions
            # start with the highest peaks and apply gaussians?
            gauss_denoised = ndimage.gaussian_filter(data, 2)
            pyplot.figure(2)
            #gauss_denoised = gauss_denoised[0:rows] 
            pyplot.plot(range(rows), gauss_denoised, label=(str(s) + '-'+ str(j+1)))
            pyplot.legend(loc='best')
            pyplot.xlabel('Axial Direction (pixels)')
            pyplot.ylabel('Average Intensity (counts/sec)')
    
    
            maxPeaks, minPeaks = peakdetect.peakdetect(gauss_denoised, range(rows), 1, 1)

#            # find 1st moment of a gaussian around each peak
#            moments = []
#            for peak in maxPeaks:
#               print 'peak: ',peak[0] 
#               minRange = peak[0] - 2*typicalIonDiameter
#               maxRange = peak[0] + 2*typicalIonDiameter
#               print 'range: ', minRange, maxRange
#               peakData = gauss_denoised[minRange:maxRange]
#               X = np.arange(minRange, maxRange)
#               peakMean = np.sum(X*peakData)/np.sum(peakData)
#               peakWidth = np.sqrt(abs(np.sum((X-peakMean)**2*peakData)/np.sum(peakData))) 
#               moments.append(peakWidth)
#            
#            print moments
            outlyingPeaks = []
            
            # find outlyers                
            for q in maxPeaks:
                if q[1] < minimumIonIntensity:
                    outlyingPeaks.append(q)                
            
            # remove outlyers
            peaks = []
            for r in maxPeaks:
                if r in outlyingPeaks:
                    pass
                else:
                    peaks.append(r)
            
            print 'Number of ions for: ' + str(s) + '-' + str(j) + ': ' + str(len(peaks)) 
                        
            numberOfIons.append(len(peaks))
            
            graphIonDistances = []
            for i in range(len(peaks) - 1):
                graphIonDistances.append(peaks[i+1][0] - peaks[i][0])
                
            #print 'Average Ion distance: ', np.mean(graphIonDistances)
            ionDistances.append(np.mean(graphIonDistances))
                
            matshow(rawdata)    
            
        except IOError:
            print 'what?'
            #print 'failed', j+1
print 'Average number of ions: ', np.mean(numberOfIons)
print 'Average Ion distance: ', np.mean(ionDistances)
pyplot.figure(3)
pyplot.plot(range(len(numberOfIons)), numberOfIons)
pyplot.xlabel('Image Number')
pyplot.ylabel('Number of Ions')

show()