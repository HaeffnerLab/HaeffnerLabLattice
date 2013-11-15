from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg


Omega_array = np.array([0.1])
Delta_array = np.linspace(-3,3,50)
theta = np.pi/2.0
gamma_array = np.array([0.0])
delta_array = np.array([0.5])#np.linspace(0.0,1.0,5)
p = 0.93565
time_array = np.linspace(0,50.0,10)

def get_A(Omega, Delta, theta, gamma, delta, p):
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
	return A