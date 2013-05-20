import labrad
import numpy as np
import matplotlib

from matplotlib import pyplot
from scipy.optimize import curve_fit
from scipy.stats import chi2

cxn = labrad.connect()
dv = cxn.data_vault
#datasets = ['2105_00','2112_12', ('2121_24','2123_16')]

dv.cd(['','Experiments','729Experiments','RamseyDephase','2012Dec20','2105_00'])
dv.open(1)
data1 = dv.get().asarray.transpose()

dv.cd(['','Experiments','729Experiments','RamseyDephase','2012Dec20','2112_12'])
dv.open(1)
data2 = dv.get().asarray.transpose()



dv.cd(['','Experiments','729Experiments','RamseyDephase','2012Dec20','2121_24'])
dv.open(1)
data3_1 = dv.get().asarray

dv.cd(['','Experiments','729Experiments','RamseyDephase','2012Dec20','2123_16'])
dv.open(1)
data3_2 = dv.get().asarray

data3 = np.concatenate((data3_1,data3_2), axis = 0).transpose()

figure = pyplot.figure()
pyplot.title('Ramsey Fringes')
pyplot.plot(data1[0],data1[1], 'k', label = 'S+1/2D+1/2 with line triggering 2012Dec20 2105_00')
pyplot.plot(data2[0],data2[1], 'b', label = 'S+1/2D+1/2 with no line triggering 2012Dec20 2112_12')
pyplot.plot(data3[0],data3[1], 'r', label = 'S+1/2D+5/2 with line triggering 2012Dec20 2121_24 + 2123_16')


pyplot.ylabel('Excitation Probability')
pyplot.xlabel(r'Delay Time between two $\pi / 2$ pulses, $\mu s$')
pyplot.legend()
pyplot.show()