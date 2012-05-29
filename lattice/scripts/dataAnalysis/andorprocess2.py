import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import *
from matplotlib import pyplot
from scipy import ndimage
import peakdetect

numberOfIons = []

typicalIonDiameter = 6 # compare sections of this size in the image
minimumIonIntensity = 3300

choose = range(20) #[12, 14]

# loop through all the files
for s in choose:
    for j in range(2):
        #j = 4
        try:   
            #rawdata = np.loadtxt('/home/lattice/Downloads/andorimages/andorprocess/s' + str(j+1) + '.asc')
            rawdata = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-5ions\s' + str(s) + '000' + str(j+1) + '.asc')
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
            data = np.sum(procdata, 1)
            
            pyplot.figure(1)
            pyplot.plot(range(rows), data, label=str(j+1))
            #matshow(rawdata)
            
            # find the number of ions
            # start with the highest peaks and apply gaussians?
            gauss_denoised = ndimage.gaussian_filter(data, 2)
            pyplot.figure(2)
            gauss_denoised = gauss_denoised[0:rows] 
            pyplot.plot(range(rows), gauss_denoised, label=(str(s) + '-'+ str(j+1)))
            pyplot.legend(loc='best')
    
    
            maxPeaks, minPeaks = peakdetect.peakdetect(gauss_denoised, range(rows), 2, 25)
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
            #matshow(rawdata)
        except IOError:
            pass
            #print 'failed', j+1
print 'Average number of ions: ', np.mean(numberOfIons)
show()