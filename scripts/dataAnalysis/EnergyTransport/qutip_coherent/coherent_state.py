import qutip
import numpy as np
from matplotlib import pyplot
from scipy.special.orthogonal import eval_genlaguerre as laguerre
import time

hilbert_space_dimension = 1000
temperature_init = 3.0
displacement_nbar = 5.0
displacement_alpha = np.sqrt(displacement_nbar)


# t1 = time.time()
# thermal_dm = qutip.thermal_dm(hilbert_space_dimension, temperature_init)
# displace_operator = qutip.displace(hilbert_space_dimension, displacement_alpha) 
# displaced_dm = displace_operator * thermal_dm * displace_operator.dag()
# diag = displaced_dm.diag()
# print time.time() - t1


# pyplot.plot(diag, 'x')

t1 = time.time()
l = [1./ (temperature_init + 1) * (temperature_init / (temperature_init + 1.0))**n * laguerre(n, 0 , -displacement_nbar / ( temperature_init * (temperature_init + 1))) * np.exp( -displacement_nbar / (temperature_init + 1)) for n in range(1000)]
arr = np.array(l)
print time.time() - t1

t1 = time.time()
def displaced_thermal_population(n):
    return 1./ (temperature_init + 1) * (temperature_init / (temperature_init + 1.0))**n * laguerre(n, 0 , -displacement_nbar / ( temperature_init * (temperature_init + 1))) * np.exp( -displacement_nbar / (temperature_init + 1))
arr = np.fromfunction(displaced_thermal_population , (1000,))
print time.time() - t1
# pyplot.title('Init temperature 3nbar', fontsize = 16)
# pyplot.suptitle('Displaced Thermal States', fontsize = 20)
# pyplot.legend()
# pyplot.show()