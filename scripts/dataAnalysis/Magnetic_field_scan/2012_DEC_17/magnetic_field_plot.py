from matplotlib import pyplot
import numpy as np

data = np.loadtxt(open("weekend_DEC_2012.csv"),delimiter=";",skiprows=1,usecols = (2,3,4,5,6))
data_avg = np.sum(data,axis=1)/5
#print np.arange(0,np.size(data_avg))
figure = pyplot.figure()
figure.clf()
pyplot.plot(np.arange(0,np.size(data_avg)),data_avg)
pyplot.show()