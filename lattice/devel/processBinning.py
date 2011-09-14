#import labrad
import numpy

file = open('C:\\test2.csv') 
print file
rawdata = numpy.array(numpy.loadtxt(file, delimiter = ','), dtype = numpy.int32)
print rawdata.shape
print rawdata[0]
print 'done'

arrayLength = 1249792
timeLength = 0.1
timeResolution = 5*10**-9 