totalfft = numpy.zeros(9998337, dtype = numpy.int32) 
last = 0

for index in range(len(q)):
	print index
	pos = positionsNZ[last:q[index]]
	el = elems[last:q[index]]
	last = q[index]
	el = map(converter , el);
	result = numpy.zeros(( arrayLength, 16), dtype = numpy.uint8) 
	result[pos] = el
	del(pos)
	del(el)
	result = result.flatten()
	fft = numpy.fft.rfft(result)
	freqs = numpy.fft.fftfreq(result.size, d = float(timeResolution))
	freqs = numpy.abs(freqs[0:result.size/2 + 1])
	del(result)
	ampl = numpy.abs(fft)
	del(fft)
	totalfft = totalfft + ampl
	del(ampl)
	numpy.save('processed{}'.format(index),totalfft)

	



	

import numpy
path = 'C:\\Python26\\Lib\\idlelib\\__data__\\Time Resolved Counts.dir\\firsttrace38.csv'
f = open(path)
raw = numpy.loadtxt(f, delimiter = ',', dtype=numpy.int32)
measuredData = raw.transpose()
positionsNZ = measuredData[0]
elems = measuredData[1]
q = []
for index in range(positionsNZ.size - 1):
	if positionsNZ[index] > positionsNZ[index+1]:
		q.append(index)

arrayLength = 1249792
timeLength = 0.1
timeResolution = 5*10**-9

import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
figure = pyplot.figure()
figure.clf()
fft = numpy.load('processed10.npy')
pyplot.plot(fft)
pyplot.savefig('processed10')

for j in range(2,9):
	figure.clf()
	fft = numpy.load('processed{}.npy'.format(j))
	pyplot.plot(fft)
	pyplot.savefig('processed{}'.format(j))

