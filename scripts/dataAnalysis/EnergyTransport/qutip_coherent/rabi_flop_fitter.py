"""
Fitter for Carrier and Sideband Rabi Flopping
"""
from motional_distribution import motional_distribution as md
import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguerre

class rabi_flop_time_evolution(object):
    
    def __init__(self, sideband_order, eta, nmax = 5000):
        self.sideband_order = sideband_order #0 for carrier, 1 for 1st sideband etc
        self.eta = eta
        self.nmax = nmax
        self.rabi_coupling = self.compute_rabi_coupling()
        
    def compute_rabi_coupling(self):
        order = self.sideband_order
        eta = self.eta
        n = np.arange(0, self.nmax) #how many vibrational states to consider
        #lists of the generalized laguere polynomails of the corresponding order evaluated at eta**2
        L = np.array([laguerre(i, order, eta**2) for i in n])
        if self.sideband_order == 0:
            omega = L * np.exp(-1./2*eta**2)
        elif self.sideband_order == 1:
            omega = L* np.exp(-1./2*eta**2)*eta**(1)*(1/(n+1.))**0.5
        elif self.sideband_order == 2:
            omega = L* np.exp(-1./2*eta**2)*eta**(2)*(1/((n+1.)*(n+2)))**0.5 
        elif self.sideband_order == 3:
            omega = L* np.exp(-1./2*eta**2)*eta**(3)*(1/((n+1.)*(n+2)*(n+3)))**0.5 
        elif self.sideband_order == 4:
            omega = np.exp(-1./2*eta**2)*eta**(4)*(1/((n+1.)*(n+2)*(n+3)*(n+4)))**0.5
        else:
            raise NotImplementedError("Can't do that high of sideband order")
        return omega
        
    def compute_evolution_thermal(self, nbar, delta, time_2pi, t, excitation_scaling = 1.):
        '''returns the state evolution for temperature nbar, detuning delta, rabi frequency T_Rabi for times t'''
        if 5 * nbar > self.nmax:
            print 'WARNING, trying to calculate nbar that is high compared to the precomputed energy levels' 
        omega = self.rabi_coupling
        ones = np.ones_like(t)
        p_n = md.thermal(nbar, self.nmax) 
        result = np.outer(p_n*omega/np.sqrt(omega**2+delta**2), ones) * (np.sin( np.outer( np.sqrt(omega**2+delta**2)*np.pi/time_2pi, t ))**2)
        result = np.sum(result, axis = 0)
        result = excitation_scaling * result
        return result