from __future__ import division
import numpy as np
from matplotlib import pyplot


Omega = 0.00001
Delta_array = np.array([0.0,0.05,0.1])
theta = np.pi/2.0
gamma_array = np.array([0.0])
# change to magnetic field
delta_array = np.arange(-3.0,3.0,0.01)
p = 0.93565

def get_coherence(Omega, Delta, theta, gamma, delta, p):
	A = np.array([[0, 0, -(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (1 + np.cos(theta)), 0, 0, 0, 0, 
  (1/2.0)*1j*Omega* np.sin(theta), 0, -(p/3), 0, 
  (1/2.0)*1j*Omega* (1 + np.cos(theta)), 0, 0, -((2.0*p)/3)], [0, 
  1j*(-delta + Delta) - 
   1j*(delta + Delta), -(1/2.0)
     *1j*Omega* (-1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 0, 0, 0, 0, 
  (1/2.0)*1j*Omega* np.sin(theta), 0, -(p/3), 0, 
  (1/2.0)*1j*Omega* (1 + np.cos(theta)), 0, 
  0], [-(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (-1 + np.cos(theta)), 
  1/2 + gamma + (1j*delta)/3 + 1j*(-delta + Delta), 
  0, 0, 0, 0, 0, 0, 0, (1/2.0)*1j*Omega* np.sin(theta), 0, 0, 0, 
  (1/2.0)*1j*Omega* (1 + np.cos(theta)), 
  0], [-(1/2.0)*1j*Omega*(1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 
  1/2 + gamma - (1j*delta)/3 + 1j*(-delta + Delta), 
  0, 0, 0, 0, 0, 0, 0, (1/2.0)*1j*Omega* np.sin(theta), 0, 0, 0, 
  (1/2.0)*1j*Omega* (1 + np.cos(theta))], [0, 0, 0, 
  0, -1j*(-delta + Delta) + 
   1j*(delta + Delta), 
  0, -(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* (-1 + np.cos(theta)), 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), 0, -(p/3), 0], [0, 0, 0, 
  0, 0, 0, -(1/2.0)*1j*Omega*(-1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 
  (1/2.0)*1j*Omega* (-1 + np.cos(theta)), -((2.0*p)/3), 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), 0, -(p/3)], [0, 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (-1 + np.cos(theta)), 
  1/2 + gamma + (1j*delta)/3 + 1j*(delta + Delta), 0,
   0, 0, (1/2.0)*1j*Omega* (-1 + np.cos(theta)), 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), 0], [0, 0, 0, 
  0, -(1/2.0)*1j*Omega*(1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 
  1/2 + gamma - (1j*delta)/3 + 1j*(delta + Delta), 0,
   0, 0, (1/2.0)*1j*Omega* (-1 + np.cos(theta)), 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta)], [1/
   2 *1j*Omega* np.sin(theta), 0, 0, 0, 
  (1/2.0)*1j*Omega* (-1 + np.cos(theta)), 0, 0, 0, 
  1/2 + gamma - (1j*delta)/3 - 1j*(-delta + Delta), 
  0, -(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (1 + np.cos(theta)), 0, 0, 0, 0], [0, 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 0, 0, 
  (1/2.0)*1j*Omega* (-1 + np.cos(theta)), 0, 0, 0, 
  1/2 + gamma - (1j*delta)/3 - 
   1j*(delta + Delta), -(1/2.0)
     *1j*Omega* (-1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 0, 0, 0], [0, 0, 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 0, 0, 
  (1/2.0)*1j*Omega* (-1 + np.cos(theta)), 
  0, -(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (-1 + np.cos(theta)), 1, 0, 0, 0, 0, 0], [0, 0,
   0, (1/2.0)*1j*Omega* np.sin(theta), 0, 0, 0, 
  (1/2.0)*1j*Omega* (-1 + np.cos(theta)), -(1/2.0)
     *1j*Omega* (1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 1 - (2*1j*delta)/3, 0, 0, 
  0, 0], [(1/2.0)*1j*Omega* (1 + np.cos(theta)), 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), 0, 0, 0, 0, 0, 0, 0, 
  1/2 + gamma + (1j*delta)/3 - 1j*(-delta + Delta), 
  0, -(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (1 + np.cos(theta))], [0, 
  (1/2.0)*1j*Omega* (1 + np.cos(theta)), 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), 0, 0, 0, 0, 0, 0, 0, 
  1/2 + gamma + (1j*delta)/3 - 
   1j*(delta + Delta), -(1/2.0)
     *1j*Omega* (-1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta)], [0, 0, 
  (1/2.0)*1j*Omega* (1 + np.cos(theta)), 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), 0, 0, 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), -(1/2.0)
     *1j*Omega* (-1 + np.cos(theta)), 1 + (2*1j*delta)/3, 
  0], [0, 0, 0, (1/2.0)*1j*Omega* (1 + np.cos(theta)), 0, 0, 
  0, -(1/2.0)*1j*Omega*np.sin(theta), 0, 0, 0, 
  0, -(1/2.0)*1j*Omega*(1 + np.cos(theta)), 
  (1/2.0)*1j*Omega* np.sin(theta), 0, 1]])
	B = np.linalg.inv(A)
	BB = B[:,0]
	signal = BB[11]-BB[14]
	return signal

for gamma in gamma_array:
	for Delta in Delta_array:	
		signal_array = []
		for delta in delta_array:
			signal = get_coherence(Omega,Delta, theta, gamma,delta,p).imag
			signal_array = np.append(signal_array,signal)
		pyplot.plot(2.0*delta_array/3.0,signal_array)

pyplot.show()