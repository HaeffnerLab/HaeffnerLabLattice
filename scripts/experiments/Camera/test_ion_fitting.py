import numpy as np
from ion_fitting import linear_chain_fitter
# import time

#load the full image and truncate it to to test image procesing of a partial image
# image = np.load('single.npy')
image = np.load('chain.npy')
image = np.reshape(image, (496, 658))
image = image[200:299, 300:400]

x_axis = np.arange(300,400)
y_axis = np.arange(200,299)

#perform the fitting routine
fitter = linear_chain_fitter()
xx,yy = np.meshgrid(x_axis, y_axis)

result, params = fitter.guess_parameters_and_fit(xx, yy, image, 8)
fitter.report(params)

import time
t1=  time.time()
state, chi_diffs = fitter.state_detection(xx, yy, image, params)
print time.time() - t1

# print state
# print chi_diffs

# fitter.report(params)
fitter.graph(x_axis, y_axis, image, params, result)
# for number in range(1, 15):
#     result, params = fitter.guess_parameters_and_fit(xx, yy, image, number)
#     print number, result.redchi
#     fitter.graph(x_axis, y_axis, image, params, result)