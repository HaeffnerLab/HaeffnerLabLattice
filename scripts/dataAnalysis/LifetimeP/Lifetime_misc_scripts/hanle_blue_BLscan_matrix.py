from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg


Omega_array = np.array([0.001])
Delta_array = np.linspace(-3,3,50)
theta = np.pi/2.0
gamma_array = np.array([0.0])
delta_array = np.array([0.0])#np.linspace(0.0,1.0,5)
p = 0.93565
time_array = np.linspace(0,50.0,10)

def get_coherence_right(Omega, Delta, theta, gamma, delta, p, time):
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
	B = linalg.expm(-A*time)
	BB = B[:,0]
	signal = (BB[15]+BB[11]).real+(BB[11]-BB[14]).imag
	return signal

def get_coherence_left(Omega, Delta, theta, gamma, delta, p, time):
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
	B = linalg.expm(-A*time)
	BB = 0.5*B[:,0]+0.5*B[:,5]
	signal = (BB[15]+BB[11]).real#+(BB[11]-BB[14]).imag
	return signal

for Omega in Omega_array:
	for gamma in gamma_array:
		
		for delta in delta_array:	
			count_array = []
			for Delta in Delta_array:
				signal_array_right = []
				signal_array_left = []
				for time in time_array:
					#signal_right = get_coherence_right(Omega,Delta, theta, gamma,delta,p,time)
					signal_left = get_coherence_right(Omega,Delta, theta, gamma,delta,p,time)
					#signal_array_right = np.append(signal_array_right,signal_right)
					signal_array_left = np.append(signal_array_left,signal_left)
				#pyplot.plot(time_array,signal_array_right)
				#pyplot.plot(time_array,signal_array_left)
				signal = np.sum(signal_array_left)#+np.sum(signal_array_right)
				count_array.extend(np.array([signal]))	
			pyplot.plot(Delta_array,count_array)

pyplot.show()