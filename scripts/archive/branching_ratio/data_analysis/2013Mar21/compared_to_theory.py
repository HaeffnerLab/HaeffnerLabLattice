#plot the binned timetags

import numpy as np
import matplotlib

from matplotlib import pyplot

Arora = np.array([0.9350])
Liaw2 = np.array([0.9366])
Sahoo = np.array([0.9373])
Guet = np.array([0.9391])
Liaw1 = np.array([0.9444])
Experiment = np.array([0.93567])

pyplot.plot(Arora,np.array([1.1]),'D',markersize=10.0,color='#003366')
pyplot.plot(Liaw2,np.array([1.2]),'o',markersize=10.0,color='#330066')
pyplot.plot(Sahoo,np.array([1.3]),'<',markersize=10.0,color='#000000')
pyplot.plot(Guet,np.array([1.4]),'*',markersize=10.0,color='#336600')
pyplot.plot(Liaw1,np.array([1.5]),'>',markersize=10.0,color='#003300')
pyplot.plot(Experiment,np.array([1.0]),'s',markersize=10.0,color='#ff0000')
pyplot.show()