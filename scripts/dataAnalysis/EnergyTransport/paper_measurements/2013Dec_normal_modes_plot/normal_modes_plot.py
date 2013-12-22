from matplotlib import pyplot
import numpy as np


#these are derives in the mathematica notebook
c5 = np.array([0.447214, 0.639533, 0.537654, 0.301658, 0.10454])
c15 = np.array([0.258199, 0.442454, 0.512446, 0.476969, 0.378185, 0.2621, 0.160762, \
0.0877321, 0.042612, 0.0183437, 0.00693382, 0.00226348, 0.000619774, \
0.000134552, 0.0000201014])
c25 = np.array([0.2, 0.360198, 0.450781, 0.465641, 0.421263, 0.343152, 0.255558, \
0.175642, 0.112078, 0.0666595, 0.0370431, 0.0192576, 0.00936861, \
0.00426249, 0.00181103, 0.000716806, 0.000263364, 0.0000893834, \
0.0000278343, 7.87943*10**-6, 2.00114*10**-6, 4.47118*10**-7, 
 8.51612*10**-8, 1.30453*10**-8, 1.39272*10**-9])


markersize = 7
pyplot.plot(1 + np.arange(5), c5, 'o', label = '5 ions', markersize = markersize)
pyplot.plot(1 + np.arange(15),c15,'v', label = '15 ions', markersize = markersize)
pyplot.plot(1 + np.arange(25),c25, 'D', label = '25 ions', markersize = markersize)
pyplot.legend(fontsize = 20)
fig = pyplot.gcf()
ax = pyplot.gca()
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
pyplot.savefig('excited_normal_modes.pdf', dpi = 600)

pyplot.show()

