import numpy as np
# from ion_fitting import linear_chain_fitter
from ion_state_detector import ion_state_detector

#load the full image and truncate it to to test image procesing of a partial image
# image = np.load('single.npy')

image = np.load('chain.npy')
image = np.reshape(image, (496, 658))
image = image[242:255, 310:390]

x_axis = np.arange(310,390)
y_axis = np.arange(242,255)
xx,yy = np.meshgrid(x_axis, y_axis)


shaped_image = image.reshape((1,13,80))
series_of_images = np.repeat(shaped_image, 100, axis = 0)

detector = ion_state_detector(8)
result, params = detector.guess_parameters_and_fit(xx, yy, image)
detector.state_detection(image)
detector.report(params)
detector.graph(x_axis, y_axis, image, params, result)

best_states, confidences = detector.state_detection(series_of_images)
excitation_probability = 1 - best_states.mean(axis = 0)
print excitation_probability, confidences