import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from ion_fitting import linear_chain_fitter

#load the full image and truncate it to to test image procesing of a partial image
image = np.load('sample_image.npy')
image = np.reshape(image, (496, 658))
image = image[200:300, 300:400]
x_axis = np.arange(200,300)
y_axis = np.arange(300,400)
# pyplot.contourf(image)
#perform the fitting routine
fitter = linear_chain_fitter()
xx,yy = np.meshgrid(x_axis, y_axis)
result, params = fitter.guess_parameters_and_fit(xx, yy, image, 1)
fitter.report(params)
fitter.graph(x_axis, y_axis, image, result)