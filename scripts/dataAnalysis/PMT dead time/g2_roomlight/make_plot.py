from matplotlib import pyplot
import numpy as np

resolution = 10 #nanoseconds

g2 = np.load('g2.npy')
kk = np.arange(g2.size) * resolution
pyplot.figure()
pyplot.bar(kk, g2, width = resolution, fill = False, edgecolor ='blue')
pyplot.xlim(xmin = 0, xmax = 200)
pyplot.xlabel('ns')
pyplot.title('g(2) measurement, room light, 100KC/sec')

#simple calculation of dead time
far_level = np.mean(g2[50:])
dead_time = np.sum(far_level - g2[0:3]) * resolution
pyplot.axhline(1, 0, 1000, color='black', lw = 2)
pyplot.annotate('dead time ~{0:.0f} ns'.format(dead_time), (5, 1.1))

pyplot.show()