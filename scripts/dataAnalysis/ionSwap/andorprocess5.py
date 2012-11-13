import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from scipy import optimize
from scipy.interpolate import interp1d
from pylab import *
from matplotlib import pyplot
from scipy import ndimage
import peakdetect
from scipy.stats import chisquare
import time
from itertools import product

positionDict = {
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


class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value

def fit(function, parameters, expectedNumberOfIons, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x, expectedNumberOfIons)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    optimize.leastsq(f, p)

def fitFunction(x, expectedNumberOfIons):
    global alpha
    global beta
    global offset
    global height
    global sigma     
    fitFunc = 0
    for i in positionDict[str(expectedNumberOfIons)]:
        fitFunc += height()*exp(-(((x-i*alpha() - beta())/sigma())**2)/2)
#    fitFunc = offset() + height()*exp(-(((x+1.7429*alpha())/sigma())**2)/2) + height()*exp(-(((x+0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x)/sigma())**2)/2) + height()*exp(-(((x-0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x-1.7429*alpha())/sigma())**2)/2)
    return fitFunc + offset()

def GetPeakPositionCatalog(numSet, numKin, rows, cols, typicalIonDiameter, iterations, expectedNumberOfIons):
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
    
    numSet = 11
    
    numberImagesInSet = (numKin / iterations)
    numberImagesToAnalyze = (numKin / iterations) - 1
          

#        # ion swap
    arr = [[] for i in range(3)]
    for j in range(3):
        arr[j] = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062812\7\image-1-' + str(3*numSet + j + 1))
#        arr[j] = np.loadtxt('image-1-' + str(3*numSet + j + 1))
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
            mostIntenseDataSums = np.sum(mostIntenseData, 0)# / typicalIonDiameter #1D vector
            mostIntenseDataSums = (mostIntenseDataSums - np.min(mostIntenseDataSums))/(np.max(mostIntenseDataSums) - np.min(mostIntenseDataSums))
            
            """
                      |      |      |      |      |
                _____/|\____/|\____/|\____/|\____/|\_____   background image sum
                
                
                ___________________   ___________________   dark ion image sum (background subtracted out)
                                   \|/
                                    |
            
            """
            
            sumArray.append(mostIntenseDataSums)

        # start here
        xmodel = np.arange(len(sumArray[0]), dtype=float)

        global alpha
        global beta
        global offset
        global height
        global sigma        
        alpha = Parameter(15)
        beta = Parameter(33)
        offset = Parameter(np.min(sumArray[0]))
#        print 'offset guess: ', offset()
        height = Parameter(np.max(sumArray[0]) - np.min(sumArray[0]))
#        print 'height guess: ', height()       
        sigma = Parameter(5)        

#        initialYmodel = fitFunction(xmodel, expectedNumberOfIons)
#        pyplot.plot(xmodel, initialYmodel)
        
#        print xmodel
#        testModel = 600 + 650*exp(-(((xmodel-14)/5)**2)/2) + 650*exp(-(((xmodel-50)/5)**2)/2)
#        print testModel
#        print 600 + 650*exp(-(((17-14)/5)**2)/2)
#        pyplot.plot(xmodel, testModel)
        fit(fitFunction, [alpha, beta, offset, height, sigma], expectedNumberOfIons, sumArray[0])
        print 'alpha: ', alpha()
        print 'beta: ', beta()
        print 'offset: ', offset()
        print 'height: ', height()
        print 'sigma: ', sigma()
        
        ymodel = fitFunction(xmodel, expectedNumberOfIons)
        
        pyplot.plot(xmodel,sumArray[0])
        pyplot.plot(xmodel, ymodel)
        
        # check the goodness of fit of individual gaussians to each peak
#        for i in positionDict[str(expectedNumberOfIons)]:
#            ionPosition = beta() + i*alpha()
#            print ionPosition
#            xmodelIndividualGaussian = np.arange(int(ionPosition - 2*sigma()),int(ionPosition + 2*sigma()))
#            print xmodelIndividualGaussian 
#            individualGaussian = offset() + height()*exp(-(((xmodelIndividualGaussian-i*alpha() - beta())/sigma())**2)/2)           
#            t1 = time.clock()
#            print chisquare(sumArray[0][ionPosition - 2*sigma():ionPosition + 2*sigma()], individualGaussian)
#            t2 = time.clock()
#            print 'time to chi: ', (t2-t1)
#            pyplot.plot(xmodelIndividualGaussian, individualGaussian)
        for q in range(2):
            t1 = time.clock()
            bestChiSquare = float(10000000)
            bestChiSquareArray = []
            chiSquareArray = []
            positionValues = positionDict[str(expectedNumberOfIons)]
            bestDarkModel = []
            secondBestDarkModel = []
            for i in product(range(2), repeat=expectedNumberOfIons):
                # build the model function
                darkModel = 0
                for j in np.arange(expectedNumberOfIons):
                    if i[j] == 1:
                        #print i, j
                        darkModel += height()*exp(-(((xmodel-positionValues[j]*alpha() - beta())/sigma())**2)/2)
                
                darkModel += offset()
                
                try:
                    tempChiSquare, pValue = chisquare(sumArray[q+1], darkModel)
                    #print tempChiSquare, pValue
                    chiSquareArray.append([tempChiSquare, i])
                    if (tempChiSquare < bestChiSquare):
                        bestChiSquare = tempChiSquare
                        bestChiSquareArray.append(bestChiSquare)
                        #print bestChiSquare, i
                        secondBestDarkModel = bestDarkModel
                        bestDarkModel = darkModel
                except AttributeError:
                    print 'loca!'
            t2 = time.clock()
            chiSquareArray.sort()
            print chiSquareArray
            print 'time: ', (t2-t1)
            print 'best: ', bestChiSquare   
#            print (bestChiSquareArray[-2] / bestChiSquareArray[-1])
#            print (bestChiSquareArray[-3] / bestChiSquareArray[-1])    
#            print (bestChiSquareArray[-3] / bestChiSquareArray[-2])
            pyplot.figure()
            pyplot.plot(xmodel, sumArray[q+1])
            pyplot.plot(xmodel, bestDarkModel, label = 'best')
            pyplot.plot(xmodel, secondBestDarkModel, label = 'runner-up')
            pyplot.legend(loc='best')
            #pyplot.figure()
            #pyplot.hist(chiSquareArray[:][0], bins=50)
            

###############-------------------------------######################

iterations = 1
typicalIonDiameter = 5 # compare sections of this size in the image

expectedNumberOfIons = 5
hstart = 455
hend = 530
vstart = 217
vend = 242
numKin = 3

rows = vend - vstart + 1
cols = hend - hstart + 1

for numSet in range(1):
    GetPeakPositionCatalog(numSet, numKin, rows, cols, typicalIonDiameter, iterations, expectedNumberOfIons)

           

show()