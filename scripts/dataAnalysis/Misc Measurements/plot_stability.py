import numpy as np
from matplotlib import pyplot

set_point = 250.0
readings = np.loadtxt('SHQ222M_stability.csv')
std = np.std(readings)
relative_stability = std / set_point

readings = 1000*(readings - set_point)



pyplot.plot(readings)

pyplot.suptitle('SHQ 222M: deviation from {}V output'.format(set_point), fontsize = 40)
pyplot.title('STD / setpoint = {0:.1e}'.format(relative_stability), fontsize = 32)
pyplot.ylabel('mV', fontsize = 32)
pyplot.xlabel('sec', fontsize = 32)
pyplot.tick_params('both', labelsize = 20)
pyplot.ylim(ymin = 0, ymax = 50)


pyplot.show()