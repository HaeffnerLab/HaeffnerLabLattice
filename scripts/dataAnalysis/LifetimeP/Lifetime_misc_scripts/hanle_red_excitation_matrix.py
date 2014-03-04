from __future__ import division
import numpy as np
from matplotlib import pyplot



Omega_array = np.array([0.0000001,0.01,0.05])
gamma_array = np.array([0.0])
# change to magnetic field
Delta_array = np.linspace(-0.1,0.1,1000)
p = 1-0.93565

def get_coherence(Omega, Delta, Gamma, gamma, p):
	A = np.array([[Gamma, 0, -(0.5)*1j*np.sqrt(3)*Omega, 
  1j*Omega, -((1j*Omega)/2), 0, 0, 0, 0, 0, 0, 0, 
  0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, -1j*Omega, 0,
   0, 0, 0, 0, (1j*Omega)/2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0], [0, Gamma - (2 *1j*Delta)/3, 
  0, -((1j*Omega)/2), 
  1j*Omega, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 
  0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0], [-(0.5)*1j*np.sqrt(3)*Omega, 
  0, gamma + Gamma/2 + (13 *1j*Delta)/15, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 
  0, 0, 0, 0, 0, 0, 0], [1j*Omega, -((1j*Omega)/2), 
  0, gamma + Gamma/2 + (1j*Delta)/15, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 
  0, 0, 0, 0, 0, 0], [-((1j*Omega)/2),1j*Omega, 0, 
  0, gamma + Gamma/2 - (11 *1j*Delta)/15, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 
  0, 0, 0, 0, 0], [0, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 
  0, gamma + Gamma/2 - (23*1j*Delta)/15, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 
  0, 0, 0, 0], [0, 0, 0, 0, 0, 0, Gamma + (2 *1j*Delta)/3, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 
  1j*Omega, -((1j*Omega)/2), 0, 0, 0, 0, 0, 0, 0, (
  1j*Omega)/2, 0, 0, 0, 0, 0, -1j*Omega, 0, 0, 0, 0,
   0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 
  0, 0, Gamma, 0, -((1j*Omega)/2), 
  1j*Omega, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 
  0, 0, (1j*Omega)/2, 0, 0, 0, 0, 0, -1j*Omega, 0, 
  0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0], [0, 0, 0, 0,
   0, 0, -(0.5)*1j*np.sqrt(3)*Omega, 
  0, gamma + Gamma/2 + (23*1j*Delta)/15, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega,
   0, 0, 0], [0, 0, 0, 0, 0, 0, 
  1j*Omega, -((1j*Omega)/2), 
  0, gamma + Gamma/2 + (11 *1j*Delta)/15, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega,
   0, 0], [0, 0, 0, 0, 0, 0, -((1j*Omega)/2), 
  1j*Omega, 0, 
  0, gamma + Gamma/2 - (1j*Delta)/15, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega,
   0], [0, 0, 0, 0, 0, 0, 0, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 
  0, gamma + Gamma/2 - (13 *1j*Delta)/15, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 0, 0, 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, 
  0.5*1j*np.sqrt(3)*Omega], [0.5*1j*np.sqrt(3)*Omega, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 - (13 *1j*Delta)/15, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 
  1j*Omega, -((1j*Omega)/2), 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 
  0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 - (23*1j*Delta)/15, 
  0, -((1j*Omega)/2), 
  1j*Omega, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [-((p*Gamma)/2), 
  0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0], [0, -((p*Gamma)/(2*np.sqrt(3))), 0, 
  0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 
  1j*Omega, -((1j*Omega)/2), 0, -((4 *1j*Delta)/5),
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0,
   0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 
  0, -((1j*Omega)/2),1j*Omega, 0, 
  0, -((8 *1j*Delta)/5), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0], [0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 
  0, 0, 0, 0, 0, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 
  0, -((12 *1j*Delta)/5), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0], [-1j*Omega, 0, 0, 0, 0, 0, (
  1j*Omega)/2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 - (1j*Delta)/15, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 
  1j*Omega, -((1j*Omega)/2), 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0], [0, -1j*Omega, 0, 0, 0, 0, 0, (
  1j*Omega)/2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 - (11 *1j*Delta)/15, 
  0, -((1j*Omega)/2), 
  1j*Omega, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0], [0, 0, -1j*Omega, 0, 0, 
  0, -((p*Gamma)/(2*np.sqrt(3))), 0, (1j*Omega)/2, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, -(0.5)*1j*np.sqrt(3)*Omega, 0, (
  4 *1j*Delta)/5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0], [-((p*Gamma)/3), 0, 0, -1j*Omega, 0, 0, 
  0, -((p*Gamma)/6), 0, (1j*Omega)/2, 0, 0, 0, 0, 
  0, 0, 0, 0,1j*Omega, -((1j*Omega)/2), 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, -((p*Gamma)/3), 
  0, 0, -1j*Omega, 0, 0, 0, 0, 0, (1j*Omega)/2, 0, 
  0, 0, 0, 0, 0, 0, -((1j*Omega)/2),1j*Omega, 0, 
  0, -((4 *1j*Delta)/5), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 
  0, 0, 0, 0, -1j*Omega, 0, 0, 0, 0, 0, (1j*Omega)/
  2, 0, 0, 0, 0, 0, 0, 0, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 
  0, -((8 *1j*Delta)/5), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [(
  1j*Omega)/2, 0, 0, 0, 0, 0, -1j*Omega, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 + (11 *1j*Delta)/15, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 
  1j*Omega, -((1j*Omega)/2), 0, 0, 0, 0, 0, 0, 
  0], [0, (1j*Omega)/2, 0, 0, 0, 0, 0, -1j*Omega, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 + (1j*Delta)/15, 
  0, -((1j*Omega)/2), 
  1j*Omega, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 
  0], [0, 0, (1j*Omega)/2, 0, 0, 0, 0, 0, -1j*Omega,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 0, (8 *1j*Delta)/5, 0, 0, 0, 
  0, 0, 0, 0, 0, 0], [0, 0, 0, (1j*Omega)/2, 0, 
  0, -((p*Gamma)/3), 0, 0, -1j*Omega, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  1j*Omega, -((1j*Omega)/2), 0, (4 *1j*Delta)/5, 0,
   0, 0, 0, 0, 0, 0, 0], [-((p*Gamma)/6), 0, 0, 0, (
  1j*Omega)/2, 0, 0, -((p*Gamma)/3), 0, 
  0, -1j*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, -((1j*Omega)/2),1j*Omega, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0], [0, -((p*Gamma)/(2*np.sqrt(3))), 0, 0, 0, (
  1j*Omega)/2, 0, 0, 0, 0, 0, -1j*Omega, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 
  0, -((4 *1j*Delta)/5), 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 
  0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 + (23*1j*Delta)/15, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 
  1j*Omega, -((1j*Omega)/2), 0], [0, 0, 0, 0, 0, 0, 
  0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, gamma + Gamma/2 + (13 *1j*Delta)/15, 
  0, -((1j*Omega)/2), 
  1j*Omega, -(0.5)*1j*np.sqrt(3)*Omega], [0, 0, 0, 0, 
  0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 0, (12 *1j*Delta)/5, 0, 0, 
  0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  1j*Omega, -((1j*Omega)/2), 0, (8 *1j*Delta)/5, 0,
   0], [0, 0, 0, 0, 0, 0, -((p*Gamma)/(2*np.sqrt(3))), 0, 0, 0,
   0.5*1j*np.sqrt(3)*Omega, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, -((1j*Omega)/2),1j*Omega, 0,
   0, (4 *1j*Delta)/5, 0], [0, 0, 0, 0, 0, 0, 
  0, -((p*Gamma)/2), 0, 0, 0, 0.5*1j*np.sqrt(3)*Omega,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, -(0.5)*1j*np.sqrt(3)*Omega, 0, 0, 0, 0]])
	B = np.linalg.inv(A)
	rho_55 = 0.25
	rho_66 = 0.25
	rho_77 = 0.25
	rho_88 = 0.25
	BB_55 = B[:,14]
	BB_66 = B[:,21]
	BB_77 = B[:,28]
	BB_88 = B[:,35]
	signal_55 = (BB_55[1]-BB_55[6]).imag + (BB_55[0]+BB_55[7]).real
	signal_66 = (BB_66[1]-BB_66[6]).imag + (BB_66[0]+BB_66[7]).real
	signal_77 = (BB_77[1]-BB_77[6]).imag + (BB_77[0]+BB_77[7]).real
	signal_88 = (BB_88[1]-BB_88[6]).imag + (BB_88[0]+BB_88[7]).real
	signal = signal_55*rho_55+signal_66*rho_66+signal_77*rho_77+signal_88*rho_88
	return signal

for Omega in Omega_array:
	for gamma in gamma_array:	
		signal_array = []
		for Delta in Delta_array:
			signal = get_coherence(Omega, Delta, 1.0, gamma, p)
			signal_array = np.append(signal_array,signal)
		pyplot.plot(2.0*Delta_array/3.0,signal_array*(1-p)/2,linewidth=2.0)
pyplot.show()