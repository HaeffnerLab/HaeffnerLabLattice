import TheoryPrediction as tp
from matplotlib import pyplot, pylab
import numpy as np
import random
from scipy import optimize
from scipy.special.orthogonal import eval_genlaguerre as laguer


maxn=1000.
omega_center=2.*np.pi*40000.
sideband_order=0
n=100
trap_frequency=1000000
fluctuations=0.1
xmax=100
nb=2

class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value
        
def fit(function, parameters, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f, p)

class StateEvolution:
    def __init__(self,nmax):
        hbar=1.054571726*10**(-34)
        m=1.660538921*40*10**(-27)
        self.eta = 2.*np.cos(np.pi/4)*np.pi/729*10**9*np.sqrt(hbar/(2.*m*2.*np.pi*trap_frequency))
        self.n=np.linspace(0,nmax,nmax+1)
        
    def omegaeff(self,omega0,sideband_order,n):#diverges for n -> infinity
        sideband_order=np.abs(sideband_order)
        x=1.
        for k in np.linspace(1,sideband_order,sideband_order):
            x=x*(n+k)
        result = self.eta**sideband_order*omega0/2.*np.exp(-self.eta**2./2.)*laguer(n,sideband_order,self.eta**2.)/np.sqrt(x)
        return result
        
    def pnb(self,nbar,sideband_order,n):#thermal state
        nplus=0.
        if sideband_order<0:
            nplus=-np.float32(sideband_order)
        result=(nbar/(nbar+1.))**(n+nplus)/(nbar+1.)
        return result

    def rabiflop(self,nbar,omega0,sideband_order,t):
        n=self.n
        result=np.sum(self.pnb(nbar,sideband_order,np.outer(n,np.ones_like(t)))*np.sin(np.outer(self.omegaeff(omega0,sideband_order,n),t))**2,axis=0)
        return result

evo=StateEvolution(maxn)
def f(x): 
    evolution = evo.rabiflop(nbar(),omega_R(),sideband_order,x)
    return evolution

nbar=Parameter(nb)
omega_R=Parameter(omega_center)    
    
flops=[]
for i in range(n):
    x=random.uniform(-1,1)*fluctuations
    sb=tp.Sideband(nb, sideband=sideband_order,omega=omega_center*(1.+x),nu=2.*np.pi*trap_frequency,amax=maxn)
    sb.anaplot(0, xmax*10**-6*sb.p.omega/(2.*np.pi), 100, 0, dephasing=False, discord=False, lsig=False)
    flops.append(sb.flop)
    print i
    
flops=np.sum(flops,axis=0)/np.float32(n)
sb.x=2.*np.pi*sb.x/sb.p.omega
m=pylab.unravel_index(np.array(flops).argmax(), np.array(flops).shape)   

fitting_region = np.where(sb.x <= 2.*sb.x[m])
p,success = fit(f, [nbar,omega_R], y = flops[fitting_region], x = sb.x[fitting_region])
    
print 'fit for nbar = {}'.format(nbar())
print 'fit for omega_R = {}'.format(omega_R())
    
sb_nondeph=tp.Sideband(nb, sideband=sideband_order,omega=omega_center,nu=2.*np.pi*trap_frequency)
sb_nondeph.anaplot(0, xmax*10**-6*sb_nondeph.p.omega/(2.*np.pi), 500, 0, dephasing=False, discord=False, lsig=False)
sb_nondeph.x=2.*np.pi*sb_nondeph.x/sb_nondeph.p.omega
    
sb_fit=tp.Sideband(nbar(), sideband=sideband_order,omega=omega_R(),nu=2.*np.pi*trap_frequency)
sb_fit.anaplot(0, xmax*10**-6*sb_fit.p.omega/(2.*np.pi), 500, 0, dephasing=False, discord=False, lsig=False)
sb_fit.x=2.*np.pi*sb_fit.x/sb_fit.p.omega

figure = pyplot.figure()    
pyplot.plot(sb.x*10**6,flops,label = 'Flops with {}% intensity fluctuations'.format(100*fluctuations))
pyplot.plot(sb_fit.x*10**6,sb_fit.flop,label = 'Fit of flops with fluctuations yields nbar = {}'.format(nbar()))
pyplot.plot(sb_nondeph.x*10**6,sb_nondeph.flop,label='Flop without intensity fluctuations, nbar = {}'.format(nb))
pyplot.legend()
pyplot.xlabel('time (us)')
pyplot.ylabel('D state occupation probability')
pyplot.show()