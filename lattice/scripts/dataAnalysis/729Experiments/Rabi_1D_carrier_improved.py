"""
Created on Mon Aug 20 13:18:06 2012
@author: expcontrol

Analyze rabi flop data of 08/23/2012 and compare to theory

"""
import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguer
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import labrad

ionnumber = 1
hbar = 1.05e-34 # J*s
mass = 40 * 1.67e-27 #kg
w = np.sqrt(ionnumber)

def lamb_dicke(wavelength, frequency, theta):
    '''computes the lamb dicke parameter
    @var theta: laser projection angle in degrees
    @var wavelength: laser wavelength in meters
    @var frequency: trap frequency in Hz
    '''
    k = 2.*np.pi/wavelength
    et = k*np.sqrt(hbar/(2*mass*2*np.pi*frequency))*np.abs(np.cos(theta*2.*np.pi / 360.0))
    return et

pump_eff = 1.0
eta = lamb_dicke(729*10**-9,2.0e6,45)/w   # axial
offset_time = 5e-6
#heating times in ms
#info = ('Carrier', [(0.0,[('2012Aug20','2312_42')])], {})
#nbar = 45; delta = 0.0; T_Rabi = 15.e-6;
#info = ('Carrier', [(10.0,[('2012Aug20','2314_26')])], {})
#nbar = 80; delta = 0.00; T_Rabi = 17.0e-6;
#info = ('Carrier', [(20.0,[('2012Aug20','2316_49')])], {})
#nbar = 110; delta = 0.0; T_Rabi = 17.5e-6;
#info = ('Carrier', [(40.0,[('2012Aug20','2319_25')])], {})
#nbar = 230; delta = 0.15; T_Rabi = 20.0e-6;
info = ('Carrier', [(50.0,[('2012Aug20','2321_53')])], {})
nbar = 270; delta = 0.15; T_Rabi = 21.0e-6;


cxn = labrad.connect('192.168.169.197')
dv = cxn.data_vault




#plots the data for all waiting times while averaging the probabilities
fig = pyplot.figure()
title,datasets,kwargs = info 
for wait_time,waitfiles in datasets:
    to_average = []
    for date,datasetName in waitfiles:
        #performs the avearing over all datasets with the same waiting time
        dv.cd( ['','Experiments','729Experiments','RabiFlopping',date,datasetName] )
        dv.open(1)  
        time,prob = dv.get().asarray.transpose()
        to_average.append(prob) 
    probs = np.array([ np.sum(x) for x in zip(*to_average) ]) / len(waitfiles)  #averaging arrays of uneven length
    time = time[0:len(probs)] # resizing time vector to correct different length sets at same waiting time!
    pyplot.plot(time, probs, '--o', label = 'heating {} ms'.format(wait_time))
    pyplot.hold(True)
    pyplot.legend()
pyplot.title(title)
pyplot.xlabel('time (us)')
pyplot.ylabel('D state occupation probability')

#analysis domain
maxt = np.max(time)
points = 100
t_increment = maxt/points
t = np.linspace(0, maxt, points)
# Distribution truncated at nmax
nmax = nbar*5 
n = np.arange(0, nmax +1)

#lists of the generalized laguere polynomails of the corresponding order evaluated at eta**2
L = np.array([laguer(i, 0, eta**2) for i in n])
L1 = np.array([laguer(i, 1, eta**2) for i in n])
L2 = np.array([laguer(i, 2, eta**2) for i in n])
L3 = np.array([laguer(i, 3, eta**2) for i in n])
L4 = np.array([laguer(i, 4, eta**2) for i in n])  
#constructing generzlied rabi coupliong strengths, see Leibfried 2003 (70)
om  = L * np.exp(-1./2*eta**2)
om1 = L1* np.exp(-1./2*eta**2)*eta**(1)*(1/(n+1.))**0.5
om2 = L2* np.exp(-1./2*eta**2)*eta**(2)*(1/((n+1.)*(n+2)))**0.5 
om3 = L3* np.exp(-1./2*eta**2)*eta**(3)*(1/((n+1.)*(n+2)*(n+3)))**0.5 
om4 = L4* np.exp(-1./2*eta**2)*eta**(4)*(1/((n+1.)*(n+2)*(n+3)*(n+4)))**0.5
#get absolute values
for arr in [om, om1, om2, om3, om4]:
    arr = np.abs(arr)
#level population probability for a given nbar, see Leibfried 2003 (57)
p = ((float(nbar)/(nbar+1.))**n)/(nbar+1.) 

ones = np.ones_like(t)
def compute_state_evolution():
    result = []
    for omega in [om , om1 , om2 , om3 ,om4]:
        res = np.outer(p*omega/np.sqrt(omega**2+delta**2), ones) * (np.sin( np.outer( np.sqrt(omega**2+delta**2)*np.pi/T_Rabi, t ))**2)
        res = np.sum(res, axis = 0)
        result.append(res)
    return result
bes,bes1,bes2,be3,bes4 = compute_state_evolution()

## approximattion \rho_{DD} in the lamb dicke regime, Roos theis (A.2)
#Omega = np.pi/T_Rabi
#x = nbar/(nbar + 1.0)
#theta = 2 * Omega * np.asarray(t)
#rho = 0.5*(1-(1/(nbar+1.))*(( (np.cos(theta)*(1. - x*np.cos(theta*eta**2))) + (x*np.sin(theta)*np.sin(theta*eta**2)) )/(1 + x**2 -2*x*np.cos(theta*eta**2))))

pyplot.plot( t + offset_time, pump_eff * bes, 'b')
pyplot.text(max(t)*0.70,0.75, 'detuning = {0}'.format(delta))
pyplot.text(max(t)*0.70,0.80, 'nbar = {0}'.format(nbar))
pyplot.text(max(t)*0.70,0.85, 'Rabi Time = {0} us'.format(10**6 * T_Rabi))
pyplot.ylim([0,1])
pyplot.legend()



#generating heating rate curve with a line fit
from scipy import optimize
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


# giving initial parameters
m = Parameter(10)
b = Parameter(50)
# define your function:
def f(x): return m() * x + b()

heating_time = np.array([0, 10, 20, 40, 50])
nbar = np.array([45, 80, 110, 230, 270])

p,success = fit(f, [m, b], y = nbar, x = heating_time)
print p,success

pyplot.figure()

pyplot.plot(heating_time, nbar, 'bo')
pyplot.plot(heating_time, f(heating_time), '-', label = 'linear fit m = {0:.1f} nbar / ms'.format(m()))
pyplot.legend()
pyplot.ylabel('nbar')
pyplot.xlabel('Time (ms)')
pyplot.show()