import sys
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from numpy import *
from scipy import optimize

IMG = raw_input("Enter the filename of the image to analyze (png): ")
IMG = str(IMG)
imageArray = plt.imread(IMG)

imageArrayRows = imageArray.shape[0]
imageArrayColumns = imageArray.shape[1]

intensityArray = [[np.float64(0)]*imageArrayColumns] * imageArrayRows
intensityArray = np.array(intensityArray)

print 'processing image'
for row in range(imageArrayRows):
    for col in range(imageArrayColumns):
        intensity = imageArray[row, col][0]*0.2989 + imageArray[row, col][1]*0.5870 + imageArray[row, col][2]*0.1140
        intensityArray[row, col] = np.float64(intensity)

print 'image processed, size: ' + str(intensityArray.shape) 


def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = sqrt(abs((arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = sqrt(abs((arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: ravel(gaussian(*p)(*indices(data.shape)) -
                                 data)
    p, success = optimize.leastsq(errorfunction, params)
    return p

data = intensityArray.transpose()

matshow(data, cmap=cm.gist_earth_r)

params = fitgaussian(data)
fit = gaussian(*params)

contour(fit(*indices(data.shape)), cmap=cm.copper)
ax = gca()
(height, x, y, width_x, width_y) = params

text(0.95, 0.05, """
x : %.1f
y : %.1f
width_x : %.1f
width_y : %.1f""" %(x, y, width_x, width_y),
        fontsize=16, horizontalalignment='right',
        verticalalignment='bottom', transform=ax.transAxes)

show()
