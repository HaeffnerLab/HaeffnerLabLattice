import numpy as np
from ion_state_detector import ion_state_detector

#load the full image and truncate it to to test image procesing of a partial image
# image = np.load('single.npy')

image = np.load('chain.npy')
image = np.reshape(image, (496, 658))
image = image[242:255, 310:390]
print image.min(), image.max()

x_axis = np.arange(310,390)
y_axis = np.arange(242,255)
xx,yy = np.meshgrid(x_axis, y_axis)


shaped_image = image.reshape((1,13,80))
series_of_images = np.repeat(shaped_image, 1, axis = 0)

detector = ion_state_detector(8)
result, params = detector.guess_parameters_and_fit(xx, yy, image)

detector.report(params)
detector.graph(x_axis, y_axis, image, params, result)


best_states, confidences = detector.state_detection(image)
excitation_probability = 1 - best_states.mean(axis = 0)
print excitation_probability, confidences

left_ion_dark_image = np.array(image)
left_ion_dark_image[:,0:10] = 793
print left_ion_dark_image.min()
detector.graph(x_axis, y_axis, left_ion_dark_image, params, result)
best_states, confidences = detector.state_detection(left_ion_dark_image)
excitation_probability = 1 - best_states.mean(axis = 0)
print excitation_probability, confidences