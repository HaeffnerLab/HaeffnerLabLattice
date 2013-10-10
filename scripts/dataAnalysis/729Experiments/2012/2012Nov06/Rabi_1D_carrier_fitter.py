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
    def __init__(self, trap_frequency, projection_angle, sideband_order, nmax = 5000, ionnumber = 1, amumass = 40, wavelength = T.Value(729, 'nm')):
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
        order = self.sideband_order
        eta = self.eta
        n = self.n
        #lists of the generalized laguere polynomails of the corresponding order evaluated at eta**2
        L = np.array([laguer(i, order, eta**2) for i in n])
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
        omega = np.abs(omega)
        return omega
        
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
        
    def compute_state_evolution(self, nbar, delta, T_Rabi, t):
        '''returns the state evolution for temperature nbar, detuning delta, rabi frequency T_Rabi for times t'''
        n = self.n
        if 5 * nbar > self.n.max():
            print 'WARNING, trying to calculate nbar that is high compared to the precomputed energy levels' 
        omega = self.rabi_coupling
        #level population probability for a given nbar, see Leibfried 2003 (57)
        ones = np.ones_like(t)
        p = ((float(nbar)/(nbar+1.))**n)/(nbar+1.) 
        result = np.outer(p*omega/np.sqrt(omega**2+delta**2), ones) * (np.sin( np.outer( np.sqrt(omega**2+delta**2)*np.pi/T_Rabi, t ))**2)
        result = np.sum(result, axis = 0)
        return result

cxn = labrad.connect('192.168.169.197')
dv = cxn.data_vault
trap_frequency = T.Value(1.1, 'MHz') #Hz
projection_angle = 45 #degrees
sideband_order = 0
pump_eff = 1.0
offset_time = 6.0e-6
flop = rabi_flop(trap_frequency = trap_frequency, projection_angle = projection_angle, sideband_order = sideband_order)

#heating times in ms
fig_title = ''
info = [
(0, 0.0, ('2012Nov06','1522_49'), 150e-6, {'nbar': Parameter(30.0), 'delta': 0.0, 'T_Rabi' : Parameter(30.4e-6)})       
#(0, 50.0, ('2012Sep28','2107_33'), 50e-6, {'nbar': 400, 'delta': Parameter(0.0), 'T_Rabi' : 15.4e-6}),
#(0, 25.0, ('2012Aug29','1857_48'), 15e-6, {'nbar': Parameter(59.0), 'delta': 0.0, 'T_Rabi' : Parameter(4.7e-6)}),
#(0, 100.0, ('2012Aug29','1903_45'), 20e-6, {'nbar': Parameter(116.0), 'delta': 0.0, 'T_Rabi' : Parameter(4.7e-6)}),
]
num_figures = len(info)

fig = pyplot.figure()
#pyplot.subplots_adjust(top = 0.95, bottom = 0, hspace = 0.15)
plots = []
ax1 = pyplot.subplot(num_figures, 1, 1)
pyplot.title(fig_title)
plots.append(ax1)

for number,trace in enumerate(info):
    if number > 0:
        ax = pyplot.subplot(num_figures,1,number + 1, sharex = ax1)
        plots.append(ax)
    order,wait_time,dataset,fit_region_max,kwargs = trace
    date,datasetName = dataset
    nbar = kwargs['nbar']
    delta = kwargs['delta']
    T_Rabi = kwargs['T_Rabi']
    #fit function definition
    def f(x): 
        #making in such that the method could be called for inputs being parameters or values
        values = []
        for param in [nbar, delta, T_Rabi]:
            if param.__class__ == Parameter:
                values.append( param() )
            else:
                values.append( param )
        nbar_value, delta_value, T_Rabi_value = values
        evolution = pump_eff * flop.compute_state_evolution( nbar_value, delta_value, T_Rabi_value, x  )
        return evolution
    #get data
    dv.cd( ['','Experiments','729Experiments','RabiFlopping',date,datasetName] )
    dv.open(1)  
    times,prob = dv.get().asarray.transpose()
    #fitting
    fitting_region = np.where((offset_time <= times) * (times <= fit_region_max))
    to_fit = [param for param in [nbar, delta, T_Rabi] if param.__class__ == Parameter] #all parameters
    p,success = fit(f, to_fit, y = prob[fitting_region], x = times[fitting_region] - offset_time)
    tmin,tmax = times[fitting_region].min(), times.max()
    detailed_times = np.linspace(tmin, tmax, 1000) 
    evolution = f(detailed_times  - offset_time)
    #plotting
    pyplot.plot(10**6 * detailed_times , evolution, 'b',linewidth=4)
    pyplot.plot(10**6 * times, prob, 'or')
#    pyplot.suptitle('Heating {} ms'.format(wait_time))
#    pyplot.ylabel('D5/2 Occupation')
    #get the final values
    values = []
    for param in [nbar, delta, T_Rabi]:
        if param.__class__ == Parameter:
            values.append( param() )
        else:
            values.append( param )
    nbar_value, delta_value, T_Rabi_value = values
    #add the values to the plot
    print wait_time
    #pyplot.annotate('heating time = {:.0f}ms'.format(wait_time), xy=(0.75, 0.8), xycoords='axes fraction')
    #pyplot.annotate('nbar = {:.0f}'.format(nbar_value).format(nbar_value), xy=(0.75, 0.7), xycoords='axes fraction')
    #pyplot.annotate('Detuning = {0}'.format(delta_value), xy=(0.75, 0.6), xycoords='axes fraction')
    #pyplot.annotate('Rabi Time = {:.1f} us'.format(10**6 * T_Rabi_value), xy=(0.75, 0.5), xycoords='axes fraction')

    #set plot limits and show
    pyplot.ylim([0,1])
    
for ax in plots[0:-1]:
    pyplot.setp(ax.get_xticklabels(), visible = False)

#rescaling x so we can see the label clearly
xmin,xmax = pyplot.xlim()
pyplot.xlim([0,150])
#pyplot.xlabel('Time us')
pyplot.show()