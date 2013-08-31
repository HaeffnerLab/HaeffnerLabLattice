import numpy as np
from ion_fitting import linear_chain_fitter
from quick_test import ion_state_detector

#load the full image and truncate it to to test image procesing of a partial image
# image = np.load('single.npy')

image = np.load('chain.npy')
image = np.reshape(image, (496, 658))
image = image[242:255, 310:390]

x_axis = np.arange(310,390)
y_axis = np.arange(242,255)
xx,yy = np.meshgrid(x_axis, y_axis)

detector = ion_state_detector(8)
result, params = detector.guess_parameters_and_fit(xx, yy, image)
detector.state_detection(image)
detector.report(params)
detector.graph(x_axis, y_axis, image, params, result)

new_detector = ion_state_detector(8)
new_detector.set_fitted_parameters(params, xx, yy)
state, confidence = new_detector.state_detection(image)
print state, confidence
