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
trap_frequency=2800000
xmax=30

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

figure = pyplot.figure()  
fluclist=np.linspace(0.01,0.10,10)
nbarlist=np.linspace(0.01, 100, 50)

for fluctuations in fluclist:
    nbarfitlist=[]

    for nb in nbarlist:
        nbar=Parameter(nb)
        omega_R=Parameter(omega_center)    
        
        flops=[]
        n1=int(n*100*fluctuations)
        for i in range(n1):
            print 'fluctuations = {:.2f}, nb = {:.2f}, i = {}'.format(fluctuations,nb,i)
            x=random.uniform(-1,1)*fluctuations
            sb=tp.Sideband(nb, sideband=sideband_order,omega=omega_center*(1.+x),nu=2.*np.pi*trap_frequency,amax=maxn)
            sb.anaplot(0, xmax*10**-6*sb.p.omega/(2.*np.pi), 50, 0, dephasing=False, discord=False, lsig=False)
            flops.append(sb.flop)
        
        flops=np.sum(flops,axis=0)/np.float32(n1)
        sb.x=2.*np.pi*sb.x/sb.p.omega
        m=pylab.unravel_index(np.array(flops).argmax(), np.array(flops).shape)   

        fitting_region = np.where(sb.x <= 2.*sb.x[m])
        p,success = fit(f, [nbar,omega_R], y = flops[fitting_region], x = sb.x[fitting_region])
        
        nbarfitlist.append(nbar())    
        
    pyplot.plot(nbarlist,nbarfitlist,label = 'Fitted nbars with {:.1%} intensity fluctuations'.format(fluctuations))

pyplot.xlabel('True nbar')
pyplot.ylabel('Apparent (fitted) nbar on carrier')
pyplot.legend(loc=2)
pyplot.show()