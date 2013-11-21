from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg

class Hanle:
	def __init__(self):
		pass

	def get_rho_dot(self,Omega, Delta, theta, gamma, delta, p, rho):
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
		rho_dot = -A.dot(np.transpose(rho))
		return rho_dot

Hanle = Hanle()
Omega = 0.1
gamma = 1.0
delta = 0.1 ## this is the Zeeman splitting
theta = np.pi/2.0
Delta = 0.0 ## this is the laser detuning
p = 0.93565
delta_t = 1.0

rho0 = np.zeros(16)
rho0[0] = 1.0

excitation = []
ground_state = []

for k in range(1,1000):
	k1 = delta_t*Hanle.get_rho_dot(Omega, Delta, theta, gamma, delta, p, rho0)
	k2 = delta_t*Hanle.get_rho_dot(Omega, Delta, theta, gamma, delta, p, rho0+k1/2.0)
	k3 = delta_t*Hanle.get_rho_dot(Omega, Delta, theta, gamma, delta, p, rho0+k2/2.0)
	k4 = delta_t*Hanle.get_rho_dot(Omega, Delta, theta, gamma, delta, p, rho0+k3)
	rho1 = rho0 + (k1+2*k2+2*k3+k4)/6.0
	rho0 = rho1
	ground_state.append(rho1[0])
	excitation.append(rho1[10]+rho1[15])

print excitation

pyplot.plot(np.real(excitation))
#pyplot.plot(np.real(ground_state))
pyplot.show()	

	
