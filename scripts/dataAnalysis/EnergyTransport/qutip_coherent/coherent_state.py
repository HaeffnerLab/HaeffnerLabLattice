import qutip
import numpy as np
from matplotlib import pyplot

hilbert_space_dimension = 5
temperature_init = 1.0
displacement_nbar = 3
displacement_alpha = np.sqrt(displacement_nbar) * 1

thermal_dm = qutip.thermal_dm(hilbert_space_dimension, temperature_init)
displace_operator = qutip.displace(hilbert_space_dimension, displacement_alpha) 
displaced_dm = displace_operator * thermal_dm * displace_operator.dag()


print displaced_dm

hilbert_space_dimension = 5
temperature_init = 1.0
displacement_nbar = 3
displacement_alpha = np.sqrt(displacement_nbar) * 1j

thermal_dm = qutip.thermal_dm(hilbert_space_dimension, temperature_init)
displace_operator = qutip.displace(hilbert_space_dimension, displacement_alpha) 
displaced_dm = displace_operator * thermal_dm * displace_operator.dag()

print displaced_dm
# diag = displaced_dm.diag()
# pyplot.plot(diag, 'x')
# pyplot.show()