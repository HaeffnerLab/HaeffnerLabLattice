import sys
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from numpy import *
from scipy import optimize

#IMG = str('c:/Users/lattice/Desktopb.png')
IMG = raw_input("enter path to image: ")
imageArray = plt.imread(IMG)
#convert RGB to intensity
intensityArray = 0.2989 * imageArray[:,:,0] + 0.5870 * imageArray[:,:,1] + 0.1140 * imageArray[:,:,2]

print 'image processed, size: ' + str(intensityArray.shape) 

def gaussian(height, center_x, center_y, width_x, width_y, offset):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: offset + height*exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = sqrt(abs((arange(col.size)-x)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = sqrt(abs((arange(row.size)-y)**2*row).sum()/row.sum())
    height = data.max()
    offset = data.min()
    return height, x, y, width_x, width_y, offset

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: ravel(gaussian(*p)(*indices(data.shape)) - data)
    p, success = optimize.leastsq(errorfunction, params)
    return p

plt.matshow(intensityArray, cmap=cm.hot)#earth_r)
params = fitgaussian(intensityArray)
fit = gaussian(*params)
contour(fit(*indices(intensityArray.shape)), cmap=cm.binary)
ax = gca()
(height, x_center, y_center, width_x, width_y, offset) = params

text(0.95, 0.05, ''''
x : %.1f
y : %.1f
width_x : %.1f
width_y : %.1f
offset : %.1f
'''%(x_center, y_center, width_x, width_y, offset),
fontsize=16, horizontalalignment='right',
verticalalignment='bottom', transform=ax.transAxes)

x = np.arange(intensityArray.shape[0])
xfit = fit(x,y_center)
xvals = intensityArray[:,int(y_center)]
y = np.arange(intensityArray.shape[1])
yfit = fit(x_center,y)
yvals = intensityArray[int(x_center),:]

plt.figure(2)
plt.title('X direction')
plt.subplot(111)
plt.plot(x, xvals, x, xfit)
plt.figure(3)
plt.title('Y direction')
plt.subplot(111)
plt.plot(y, yvals, y, yfit)

show()

