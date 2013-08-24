import qutip
import numpy as np
from matplotlib import pyplot

hilbert_space_dimension = 50
temperature_init = 3.0

for displ,color in [(0, 'k'), (5, 'b'), (10, 'g'), (20, 'r')]:
    displacement_nbar = displ
    displacement_alpha = np.sqrt(displacement_nbar)
    thermal_dm = qutip.thermal_dm(hilbert_space_dimension, temperature_init)
    displace_operator = qutip.displace(hilbert_space_dimension, displacement_alpha) 
    displaced_dm = displace_operator * thermal_dm * displace_operator.dag()
    diag = displaced_dm.diag()
    pyplot.plot(diag, 'x', color = color, label = 'displacement = {} nbar'.format(displ))

pyplot.title('Init temperature 3nbar', fontsize = 16)
pyplot.suptitle('Displaced Thermal States', fontsize = 20)
pyplot.legend()
pyplot.show()