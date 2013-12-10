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
        '''
        Rabi couplings, see Leibfried (2003), eq:70
        '''
        eta = self.eta
        if self.sideband_order == 0:
            coupling_func = lambda n: np.exp(-1./2*eta**2) * laguerre(n, 0, eta**2)
        elif self.sideband_order == 1:
            coupling_func = lambda n: np.exp(-1./2*eta**2) * eta**(1)*(1./(n+1.))**0.5 * laguerre(n, 1, eta**2)
        elif self.sideband_order == 2:
            coupling_func = lambda n: np.exp(-1./2*eta**2) * eta**(2)*(1./((n+1.)*(n+2)))**0.5 * laguerre(n, 2, eta**2)
        elif self.sideband_order == 3:
            coupling_func = lambda n: np.exp(-1./2*eta**2) * eta**(3)*(1./((n+1)*(n+2)*(n+3)))**0.5 * laguerre(n, 3 , eta**2) 
        elif self.sideband_order == 4:
            coupling_func = lambda n: np.exp(-1./2*eta**2) * eta**(4)*(1./((n+1)*(n+2)*(n+3)*(n+4)))**0.5 * laguerre(n, 4 , eta**2)
        elif self.sideband_order == 5:
            coupling_func = lambda n: np.exp(-1./2*eta**2) * eta**(5)*(1./((n+1)*(n+2)*(n+3)*(n+4)*(n+5)))**0.5 * laguerre(n, 5 , eta**2)      
        elif self.sideband_order == -1:
            coupling_func = lambda n: 0 if n == 0 else np.exp(-1./2*eta**2) * eta**(1)*(1./(n))**0.5 * laguerre(n - 1, 1, eta**2)
        elif self.sideband_order == -2:
            coupling_func = lambda n: 0 if n <= 1 else np.exp(-1./2*eta**2) * eta**(2)*(1./((n)*(n-1.)))**0.5 * laguerre(n - 2, 2, eta**2)
        elif self.sideband_order == -3:
            coupling_func = lambda n: 0 if n <= 2 else np.exp(-1./2*eta**2) * eta**(3)*(1./((n)*(n-1.)*(n-2)))**0.5 * laguerre(n -3, 3, eta**2)
        elif self.sideband_order == -4:
            coupling_func = lambda n: 0 if n <= 3 else np.exp(-1./2*eta**2) * eta**(4)*(1./((n)*(n-1.)*(n-2)*(n-3)))**0.5 * laguerre(n -4, 4, eta**2)
        elif self.sideband_order == -5:
            coupling_func = lambda n: 0 if n <= 4 else np.exp(-1./2*eta**2) * eta**(5)*(1./((n)*(n-1.)*(n-2)*(n-3)*(n-4)))**0.5 * laguerre(n -5, 5, eta**2)
        else:
            raise NotImplementedError("Can't calculate rabi couplings sideband order {}".format(self.sideband_order))
        return np.array([coupling_func(n) for n in range(self.nmax)])
        
    def compute_evolution_thermal(self, nbar, delta, time_2pi, t, excitation_scaling = 1.):
        '''returns the state evolution for temperature nbar, detuning delta, rabi frequency T_Rabi for times t'''
        omega = self.rabi_coupling
        ones = np.ones_like(t)
        p_n = md.thermal(nbar, self.nmax)
        if 1 - p_n.sum() > 1e-6:
            raise Exception ('Hilbert space too small, missing population')
        if delta == 0:
            #prevents division by zero if delta == 0, omega == 0
            effective_omega = 1
        else:
            effective_omega = omega/np.sqrt(omega**2+delta**2)
        result = np.outer(p_n * effective_omega, ones) * (np.sin( np.outer( np.sqrt(omega**2+delta**2)*np.pi/time_2pi, t ))**2)
        result = np.sum(result, axis = 0)
        result = excitation_scaling * result
        return result
    
    def compute_evolution_coherent(self, nbar, alpha, delta, time_2pi, t, excitation_scaling = 1.):
        '''returns the state evolution for temperature nbar, detuning delta, rabi frequency T_Rabi for times t'''
        omega = self.rabi_coupling
        ones = np.ones_like(t)
        p_n = md.displaced_thermal(alpha, nbar, self.nmax)
        if 1 - p_n.sum() > 1e-6:
            raise Exception ('Hilbert space too small, missing population')
        if delta == 0:
            #prevents division by zero if delta == 0, omega == 0
            effective_omega = 1
        else:
            effective_omega = np.abs(omega)/np.sqrt(omega**2+delta**2)
        result = np.outer(p_n * effective_omega, ones) * (np.sin( np.outer( np.sqrt(omega**2+delta**2)*np.pi/time_2pi, t ))**2)
        result = np.sum(result, axis = 0)
        result = excitation_scaling * result
        return result
