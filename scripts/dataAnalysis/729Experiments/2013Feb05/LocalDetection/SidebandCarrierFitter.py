"""
Fitter for Carrier and Sideband Rabi Flopping to extract Temperature.####
"""
import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguer
from scipy import optimize
import matplotlib

from matplotlib import pyplot
import labrad
from labrad import types as T, units as U

#optimization
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

#class for computing rabi flop time evolution
class rabi_flop():
    def __init__(self, trap_frequency, projection_angle, sideband_order, nmax = 1000, ionnumber = 1, amumass = 40, wavelength = T.Value(729, 'nm')):
        self.ionnumber = ionnumber
        self.trap_frequency = trap_frequency['Hz']
        self.wavelength = wavelength['m']
        self.mass = amumass * U.amu['kg']
        self.projection_angle = projection_angle
        self.sideband_order = sideband_order #0 for carrier, 1 for 1st sideband etc
        self.n = np.arange(0, nmax +1) #how many vibrational states to consider
        self.eta = self.lamb_dicke() / np.sqrt(ionnumber)
        self.rabi_coupling = self.rabi_coupling()
        
    def rabi_coupling(self):
        eta = self.eta
        n = self.n
        sideband=np.abs(self.sideband_order)
        x=1
        for k in np.linspace(1,sideband,sideband):
            x=x*(n+k)
        result = eta**sideband/2.*np.exp(-eta**2./2.)*laguer(n,sideband,eta**2.)/np.sqrt(x)
        return result
        
    def lamb_dicke(self):
        '''computes the lamb dicke parameter
        @var theta: laser projection angle in degrees
        @var wavelength: laser wavelength in meters
        @var frequency: trap frequency in Hz
        '''
        theta = self.projection_angle
        mass = self.mass
        wavelength = self.wavelength
        frequency = self.trap_frequency
        hbar = U.hbar['J*s']
        k = 2.*np.pi/wavelength
        eta = k*np.sqrt(hbar/(2*mass*2*np.pi*frequency))*np.abs(np.cos(theta*2.*np.pi / 360.0))
        return eta
        
    def compute_state_evolution(self, nbar, delta, f_Rabi, t):
        '''returns the state evolution for temperature nbar, detuning delta, rabi frequency T_Rabi for times t'''
        n = self.n
        if 5 * nbar > self.n.max():
            print 'WARNING, trying to calculate nbar that is high compared to the precomputed energy levels' 
        #level population probability for a given nbar, see Leibfried 2003 (57)
        ones = np.ones_like(t)
        sideband=self.sideband_order
        rabi_coupling = self.rabi_coupling
        nplus=0
        if sideband<0:
            nplus=-sideband
        
        p = ((float(nbar)/(nbar+1.))**(n+nplus))/(nbar+1.) 
        result = np.outer(p, ones) * (np.sin( np.outer(f_Rabi*rabi_coupling, t ))**2)
        result = np.sum(result, axis = 0)
        return result

cxn = labrad.connect('192.168.169.197')
dv = cxn.data_vault

pump_eff = 1.0
offset_time = 600e-9
sideband_order = 0
trap_frequency = T.Value(2.8, 'MHz') #Hz
projection_angle = 45 #degrees
#heating times in ms
info = ('Carrier Rabi-Flop after improving the imaging system', 0.0, ([['2013Feb05','1137_00'],['2013Feb05','1138_55']]), {})
nbar = Parameter(5); delta = 0; f_Rabi = Parameter(2.*np.pi/26e-6);
#info = ('Carrier', [(10.0,[('2012Aug20','2314_26')])], {})
#nbar = 80; delta = 0.00; T_Rabi = 17.0e-6;
#info = ('Carrier', [(20.0,[('2012Aug20','2316_49')])], {})
#nbar = 110; delta = 0.0; T_Rabi = 17.5e-6;
#info = ('Carrier', [(40.0,[('2012Aug20','2319_25')])], {})
#nbar = 230; delta = 0.15; T_Rabi = 20.0e-6;
#info = ('Carrier', 0, 50.0, ('2012Aug20','2321_53'), {})
#nbar = Parameter(270); delta = Parameter(0.15); T_Rabi = Parameter(21.0e-6);

flop = rabi_flop(trap_frequency = trap_frequency, projection_angle = projection_angle, sideband_order = sideband_order)

def f(x): 
    evolution = flop.compute_state_evolution( nbar(), delta, f_Rabi(), x  )
    return evolution


#plots the data for all waiting times while averaging the probabilities
times=[]
prob=[]
fig = pyplot.figure()
title, wait_time,dataset,kwargs = info
for i in range(len(dataset)):
    date,datasetName = dataset[i]
    dv.cd( ['','Experiments','729Experiments','RabiFlopping',date,datasetName] )
    dv.open(1)  
    addto_times,addto_prob = dv.get().asarray.transpose()
    times=np.concatenate((times,addto_times))
    prob=np.concatenate((prob,addto_prob))
#    print i,len(times)
    
tmin,tmax = times.min(), times.max()
detailed_times = np.linspace(tmin, tmax, 1000)
#evolution = flop.compute_state_evolution( nbar(), delta, T_Rabi, detailed_times - offset_time )
#pyplot.plot(detailed_times , evolution,  'b', label = 'fit')

fitting_region = np.where(times <= 200e-6)
p,success = fit(f, [nbar, f_Rabi], y = prob[fitting_region], x = times[fitting_region] - offset_time)
print 'fit for nbar is', nbar()
print 'fit to f_Rabi is ', f_Rabi()
evolution = flop.compute_state_evolution( nbar(), delta, f_Rabi(), detailed_times - offset_time )
pyplot.plot(detailed_times*10**6 , evolution,  'b', label = 'fit',linewidth=2)

pyplot.plot(times*10**6, prob, 'o', label = 'heating {} ms'.format(wait_time),color='red')

pyplot.hold(True)
pyplot.legend()
pyplot.title(title)
pyplot.xlabel('time (us)')
pyplot.ylabel('D state occupation probability')
pyplot.text(max(times)*0.85*10**6,0.78, 'detuning = {0}'.format(delta))
pyplot.text(max(times)*0.85*10**6,0.83, 'nbar = {:.2f}'.format(nbar()))
pyplot.text(max(times)*0.85*10**6,0.88, 'Rabi Frequency f = {:.1f} kHz'.format(10**-3 * f_Rabi()/(2.*np.pi)))
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()