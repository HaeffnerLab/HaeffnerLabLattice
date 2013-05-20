from __future__ import division
import numpy as np
import matplotlib
#from constants import constants as c

from matplotlib import pyplot


#in the form angle  branching fraction , error
data = [
        [0, 0.93564,  14*10**-5],#1646_36 May01
        [1, 0.93601,  15*10**-5],#1732_17 May01
        [2, 0.93594,  21*10**-5],#1820_19 May01
        [3, 0.93560,  15*10**-5],#1820_19 May01
        [4, 0.93558,  15*10**-5],#1820_19 May01
        [5, 0.93565,  5*10**-5],#1820_19 May01
        [6, 0.93565,   16*10**-5],
        [7, 0.93543,  13*10**-5],
        [8, 0.93551,  13*10**-5],
        [9, 0.93574,  17*10**-5],
        [10, 0.93574,  17*10**-5],
        [11, 0.93597,  11*10**-5],
        [12, 0.93595,  13*10**-5],
        [13, 0.93536,  17*10**-5],
        ]

data = np.array(data)
pyplot.figure()
#finding the angle 325mA corresponds to angle of 0, and then we apply 1000ma to the other axis
pyplot.errorbar(data[:,0], y = data[:,1], yerr = data[:,2], fmt = '*')
pyplot.xlabel('Measurement')
pyplot.ylabel('Branching Fraction')


pyplot.show()