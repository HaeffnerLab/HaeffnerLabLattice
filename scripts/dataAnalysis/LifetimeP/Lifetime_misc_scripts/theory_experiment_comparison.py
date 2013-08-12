import numpy as np
import lmfit
from matplotlib import pyplot
import labrad

pyplot.errorbar(np.array([1,2,3]),np.array([6.88,7.098,6.978]),np.array([0.06,0.020,0.056]),ls="None",markersize = 3.0,fmt='o')
#pyplot.plot(np.arange(-40,40,0.1),hanle_model(params,np.arange(-40,40,0.1)))
pyplot.show()