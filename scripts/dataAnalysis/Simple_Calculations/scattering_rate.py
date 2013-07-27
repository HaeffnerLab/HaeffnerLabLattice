import numpy as np

Gamma = 1. / (7.1*10**-9) #Radians / sec for Ca+ P1/2
s = 63.6834# saturation parameters
Delta = 2 * np.pi *400 *10**9#Hz


rho_ee = (s /2.) / (1 + s + ((2 * Delta) / Gamma)**2)
scattering_rate = Gamma * rho_ee
print 'scattering rate', scattering_rate
print scattering_rate * 25e-6