import matplotlib

from matplotlib import pyplot
import numpy as np

sensitive_line = np.array([
				(0, 0.937),
				(50, 0.976),
				(500, 0.825),
				(1000, 0.751),
				])

non_sensitive_line = np.array([
				(0, 0.930),
				(1000, 0.873),
				(2000, 0.853),
				(4000, 0.473),
				])
				
pyplot.plot(sensitive_line.transpose()[0], sensitive_line.transpose()[1],'b*', label = 'S-1/2D-5/2',  markersize = 10)
pyplot.plot(non_sensitive_line.transpose()[0], non_sensitive_line.transpose()[1], 'r*', label = 'S-1/2D-1/2', markersize = 10)
pyplot.ylim(0,1)
pyplot.xlim(0,5000)
pyplot.title('T2 measurement')
pyplot.xlabel('Gap Time \mus')
pyplot.ylabel('Ramsey Contrast')
pyplot.legend()
pyplot.show()