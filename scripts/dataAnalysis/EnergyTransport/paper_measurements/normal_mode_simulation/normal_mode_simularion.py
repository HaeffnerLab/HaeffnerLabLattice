import numpy as np
from matplotlib import pyplot
#input form Mathematica notebook for 5 ions
freqs = np.array([1., 0.996953, 0.992645, 0.987245, 0.980842])
populations = np.array([-0.447214, 0.639533, 0.537654, -0.301658, -0.10454])
#eigenvectors
e1 = np.array([-0.447214, -0.447214, -0.447214, -0.447214, -0.447214])
e2 = np.array([0.639533, 0.301658, 0, -0.301658, -0.639533])
e3 = np.array([0.537654, -0.280516, -0.514275, -0.280516, 0.537654])
e4 = np.array([-0.301658, 0.639533, 0, -0.639533, 0.301658])
e5 = np.array([-0.10454, 0.470437, -0.731793, 0.470437, -0.10454])

emodes = np.vstack((e1,e2,e3,e4,e5))
init_position = np.dot(populations, emodes)
# print init_position #matches [1,0,0,0,0]
start = 0
stop = 7000
steps = stop * 100 
times = np.linspace(0, stop, steps)

oscillating_populations = np.outer(np.ones_like(times), populations) * np.cos(np.outer(times , freqs))
positions = np.dot(oscillating_populations,emodes)

x1 = positions.transpose()[0]
x5 = positions.transpose()[4]
v1 = np.diff(x1)
v5 = np.diff(x5)

energy_left = v1**2
energy_right = v5**2

energy_max = energy_left.max()
energy_left = energy_left / energy_max
energy_right = energy_right / energy_max

pyplot.figure()
pyplot.plot(times[1:], energy_left)
# pyplot.plot(times[1:], energy_right)

chunksize = 5000
numchunks = energy_left.size // chunksize 
energy_left = energy_left[:chunksize*numchunks].reshape((-1, chunksize))
energy_right = energy_right[:chunksize*numchunks].reshape((-1, chunksize))
time_axis_binned = times[:chunksize*numchunks].reshape((-1, chunksize))
energy_left = energy_left.mean(axis=1)
energy_right = energy_right.mean(axis=1)
time_axis_binned = time_axis_binned.mean(axis=1)
pyplot.figure()
pyplot.plot(time_axis_binned, energy_left)
# pyplot.plot(time_axis_binned, energy_right)
pyplot.show()

# print evolution
# print evolution.shape



