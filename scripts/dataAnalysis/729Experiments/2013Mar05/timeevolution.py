import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguer
from labrad import units as U

class time_evolution():#contains all relevant functions for thermal states, rabi flops and dephasing
    def __init__(self, trap_frequency, sideband_order,nmax = 1000):
        m = 40 * U.amu
        hbar = U.hbar
        wavelength= U.WithUnit(729,'nm')
        
        self.sideband_order = sideband_order
        self.n = np.linspace(0, nmax,nmax +1)
        self.eta = 2.*np.cos(np.pi/4)*np.pi/wavelength['m']*np.sqrt(hbar['J*s']/(2.*m['kg']*2.*np.pi*trap_frequency['Hz']))
        self.rabi_coupling=self.rabi_coupling()
        
    def rabi_coupling(self):
        eta = self.eta
        n = self.n
        sideband=np.abs(self.sideband_order)
        x=1
        for k in np.linspace(1,sideband,sideband):
            x=x*(n+k)
        result = (eta**sideband)/2.*np.exp(-.5*eta**2.)*laguer(n,sideband,eta**2.)/np.sqrt(x)
        return result
        
    def p_thermal(self,nbar):
        n = self.n
        sideband = self.sideband_order
        nplus=0
        if sideband<0:
            nplus=-sideband
        #level population probability for a given nbar, see Leibfried 2003 (57)
        nbar=np.float64(nbar)
        p = ((nbar/(nbar+1.))**(n+nplus))/(nbar+1.)
        pp=np.sum(((nbar/(nbar+1.))**(np.linspace(-nplus,-1,nplus)+nplus))/(nbar+1.),axis=0)
        one=np.sum(p,axis=0)+pp
        if np.abs(1-one)>0.00001:
            print 'Warning: nmax may not be high enough for chosen value of nbar = {0}\nmissing probability = {1}'.format(nbar,1-one)
        return p
    
    def state_evolution(self, nbar, f_Rabi, t):
        ones = np.ones_like(t)
        omega_eff = self.rabi_coupling*2.0*np.pi*f_Rabi['Hz']
        p = self.p_thermal(nbar)
        result = np.sum(np.outer(p, ones) * np.sin( np.outer(omega_eff, t ))**2, axis = 0)
        return result
    
    def local_signal(self,nbar,f_Rabi,t0,t): #Local signal after local detection as a function of t
        p = self.p_thermal(nbar)
        omega_eff = self.rabi_coupling*2.0*np.pi*f_Rabi['Hz']
        result=(2.*np.abs(np.sum(np.outer(p,np.ones_like(t))*
                         np.sin(np.outer(omega_eff,np.ones_like(t))*t0)*
                         np.cos(np.outer(omega_eff,np.ones_like(t))*t0)*
                         np.sin(np.outer(omega_eff,t-np.ones_like(t0)*t0))*
                         np.cos(np.outer(omega_eff,t-np.ones_like(t0)*t0)),axis=0))**2)
        return result
    
    def deph_evolution(self,nbar,f_Rabi,t0,t):
        omega_eff = self.rabi_coupling*2.0*np.pi*f_Rabi['Hz']
        p=self.p_thermal(nbar)
        result=(np.sum(np.outer(p,np.ones_like(t))*(np.sin(np.outer(omega_eff,np.ones_like(t))*t0)**2.*np.cos(np.outer(omega_eff,t-np.ones_like(t0)*t0))**2+
                                 np.sin(np.outer(omega_eff,t-np.ones_like(t0)*t0))**2.*np.cos(np.outer(omega_eff,np.ones_like(t))*t0)**2.),axis=0))
        return result

    def discord(self,nbar,f_Rabi,t):
        omega_eff = self.rabi_coupling*2.0*np.pi*f_Rabi['Hz']
        p=self.p_thermal(nbar)
        result=(2.*np.sum(np.outer(p**2,np.ones_like(t))*np.sin(np.outer(omega_eff,t))**2*
                          np.cos(np.outer(omega_eff,t))**2,axis=0))
        return result