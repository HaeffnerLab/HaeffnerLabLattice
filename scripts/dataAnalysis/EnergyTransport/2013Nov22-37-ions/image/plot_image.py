import numpy as np
from matplotlib import pyplot

image = np.loadtxt('37_ion_local.asc',dtype = int,delimiter =',', usecols = range(1,497))
image = image.transpose()
image = image[200:275,210:430]
print image
fig,ax = pyplot.subplots()
imgplot = ax.imshow(image, cmap=pyplot.cm.gray, interpolation='nearest')
imgplot.set_clim(500,3000)
pyplot.show()