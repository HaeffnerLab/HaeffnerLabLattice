import numpy as np
import labrad
import matplotlib
from matplotlib import pyplot

# throw_away = [74, 88, 89, 128, 176, 209, 212]
throw_away = []
#get timatags from the npy file
data = np.load('locked.npy')


V1 = data[:,1]
V2 = data[:,2]
time = data[:,0]

pyplot.plot(time, V1)
pyplot.show()