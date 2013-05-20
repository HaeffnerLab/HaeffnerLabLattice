#plot the binned timetags

import numpy as np
import matplotlib

from matplotlib import pyplot

BR = np.array([0.9357,0.9357,0.9357,0.9356,0.9356,0.9357])
power = np.array([-20.01,-20,-19.99,-15,-15.01,-11])
error = np.array([0.0001,0.0001,0.0001,0.0001,0.0002,0.0002])

pyplot.errorbar(power, BR,yerr=error)
pyplot.title('Branching Ratio')

pyplot.show()