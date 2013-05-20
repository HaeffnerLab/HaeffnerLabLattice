"""
Fitter for Carrier and Sideband Rabi Flopping or Ramsey Fringes.####
"""
import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguer
from scipy import optimize
import matplotlib

from matplotlib import pyplot
import labrad
from labrad import units as U

# PROVIDE INFO FOR PLOTS
        #'dataset' has three levels: 
        #    1st level: plots which need to be averaged (NEED TO SHARE SAME TIME AXIS)
        #    2nd level: sets to be joined to one plot (CONSECUTIVE TIME AXES)
        #    3rd level: Dates and Filenames of the parts
        
info = {'plot_type':'rabi_flop',
        'title':'Carrier Rabi-Flop', 
        'sideband':1,
        'offset_time': U.WithUnit(0,'ns'),
        'trap_frequency': U.WithUnit(2.8, 'MHz'), 
        'nmax':1000,
        'fit_until':U.WithUnit(200,'us'),
        'folder':'RabiFlopping',
        #'datasets':[[['2013Feb05','1137_00'],['2013Feb05','1138_55']]],
        #'datasets':[[['2013Feb05','1433_43']],[['2013Feb05','1431_49']],[['2013Feb05','1435_40']]],
        'datasets':[[['2013Feb21','1524_20']]],
        'fit_init_nbar':1,
        'fit_init_RabiTime':U.WithUnit(175,'us'),
        'plot_initial_values':False}
#info = {
#        'plot_type':'ramsey_fringe',
#        'title':'Ramsey Fringes', 
##        'fit_from':U.WithUnit(200,'us'),
##        'fit_until':U.WithUnit(250,'us'),
#        'folder':'RamseyDephase',
#        #'datasets':[[['2013Jan17','1731_45'],['2013Jan17','1733_00']]],
#        #'datasets':[[['2012Dec20','2105_00']]],
#        #'datasets':[[['2012Dec20','2121_24'],['2012Dec20','2123_16']]],
#        'datasets':[[['2013Jan22','2325_50']]],
#        'fit_init_period':U.WithUnit(30,'us'),
#        'fit_init_T2':U.WithUnit(2000,'us'),
#        'fit_init_phase':0,
#        'fit_init_contrast':0.8,
#        'plot_initial_values':False
#        }

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
    def __init__(self, trap_frequency, sideband_order,nmax = 1000):
        m = 40 * U.amu
        hbar = U.hbar
        wavelength= U.WithUnit(729,'nm')
        
        self.sideband_order = sideband_order #0 for carrier, 1 for 1st blue sideband etc
        self.n = np.linspace(0, nmax,nmax +1) #how many vibrational states to consider
        self.eta = 2.*np.cos(np.pi/4)*np.pi/wavelength['m']*np.sqrt(hbar['J*s']/(2.*m['kg']*2.*np.pi*trap_frequency['Hz']))
        self.rabi_coupling=self.rabi_coupling()
        
    def rabi_coupling(self):
        eta = self.eta
        n = self.n
        sideband=np.abs(self.sideband_order)
        x=1
        for k in np.linspace(1,sideband,sideband):
            x=x*(n+k)
        result = eta**sideband/2.*np.exp(-eta**2./2.)*laguer(n,sideband,eta**2.)/np.sqrt(x)
        return result
        
    def state_evolution(self, nbar, f_Rabi, t):
        sideband=self.sideband_order
        nplus=0
        if sideband<0:
            nplus=-sideband
        n = self.n
        #level population probability for a given nbar, see Leibfried 2003 (57)
        p = ((float(nbar)/(nbar+1.))**(n+nplus))/(nbar+1.)
        
        if np.abs(1-np.sum(p,axis=0))>0.00001:
            print 'Warning: nmax may not be high enough for chosen value of nbar\n missing probability = {0}'.format(1-np.sum(p,axis=0))

        ones = np.ones_like(t)
        rabi_coupling = self.rabi_coupling

        result = np.outer(p, ones) * np.sin( np.outer(2.*np.pi*f_Rabi*rabi_coupling, t ))**2
        result = np.sum(result, axis = 0)
        return result

cxn = labrad.connect('192.168.169.197')
dv = cxn.data_vault

# get data, create data arrays: joining together and averaging over various data sets
dataset=info['datasets']
folder=info['folder']
prob_list=[]
for k in range(len(dataset)): #loops over all plots which have to be averaged
    times=[]
    prob=[]
    for i in range(len(dataset[k])): #each individual plot may be decomposed into several datasets which need to be joined for a complete plot
        date,datasetName = dataset[k][i]
        dv.cd( ['','Experiments','729Experiments',folder,date,datasetName] )
        dv.open(1)  
        addto_times,addto_prob = dv.get().asarray.transpose()
        times=np.concatenate((times,addto_times))
        prob=np.concatenate((prob,addto_prob))
    prob_list.append(prob)
#print times
prob=np.sum(prob_list,axis=0)/np.float32(len(dataset))

#find boundary conditions for fit 
tmin,tmax = times.min(), times.max()
detailed_times = np.linspace(tmin, tmax, 1000)
if 'offset_time' in info: 
    offset_time=info['offset_time']['s']
else:
    offset_time=0
if 'fit_until' in info: 
    fit_until=info['fit_until']['s']
else:
    fit_until=tmax
if 'fit_from' in info: 
    fit_from=info['fit_from']['s']
else:
    fit_from=tmin
fitting_region = np.where((times <= fit_until) & (times>=fit_from))

# Find out what data and fit
if info['plot_type']=='rabi_flop':
    nbar = Parameter(info['fit_init_nbar'])
    if 'sideband' in info: sideband_order=info['sideband'] 
    else: sideband_order=0
    if 'nmax' in info: nmax=info['nmax']
    else: nmax=1000
    trap_frequency = info['trap_frequency']
    flop = rabi_flop(nmax=nmax,trap_frequency = trap_frequency, sideband_order = sideband_order)
    fit_init_fRabi=1./(info['fit_init_RabiTime']['s']*(flop.eta*np.sqrt(info['fit_init_nbar']))**sideband_order)
    f_Rabi = Parameter(fit_init_fRabi)
    def f(t):
        evolution = flop.state_evolution(nbar(), f_Rabi(), t)
        return evolution
    p,success = fit(f, [nbar, f_Rabi], y = prob[fitting_region], x = times[fitting_region] - offset_time)
    print 'fit for nbar is', nbar()
    print 'fit to f_Rabi is ', f_Rabi()
    if 'plot_initial_values' in info and info['plot_initial_values']:
        evolution = flop.state_evolution( info['fit_init_nbar'], 1./info['fit_init_RabiTime']['s'], detailed_times - offset_time )
    else:
        evolution = flop.state_evolution( nbar(), f_Rabi(), detailed_times - offset_time )
    plot_fit_label = 'fit with nb = {:.2f} and f_Rabi = {:.1f} kHz'.format(nbar(),10**-3 * f_Rabi())
    plot_data_label = 'measured data, sideband = {}'.format(sideband_order)

elif info['plot_type']=='ramsey_fringe':
    def ramsey_fringe(frequency,T2,phase,contrast,offset,t):
        return contrast*np.exp(-t/T2)*(np.cos(np.pi*frequency*t+phase)**2-.5)+.5+offset
    if 'fit_init_phase' in info: fit_init_phase=info['fit_init_phase']
    else: fit_init_phase=0
    if 'fit_init_contrast' in info: fit_init_contrast=info['fit_init_contrast']
    else: fit_init_contrast=1
    frequency = Parameter(1./info['fit_init_period']['s'])
    T2 = Parameter(info['fit_init_T2']['s'])
    phase = Parameter(fit_init_phase)
    contrast = Parameter(fit_init_contrast)
    offset=Parameter(0)
    def f(t):
        evolution = ramsey_fringe(frequency(), T2(),phase(),contrast(),offset(), t)
        return evolution
    p,success = fit(f, [frequency, T2,phase,contrast,offset], y = prob[fitting_region], x = times[fitting_region] - offset_time)
    print 'fit to T2 is {} ms'.format(T2()*10**6)
    print 'fit for f is {} kHz'.format(frequency()*10**-3)
    print 'fit for contrast is {}'.format(contrast())
    print 'fit to phase is {}'.format(phase())
    print 'fit to offset is {}'.format(offset())
    if 'plot_initial_values' in info and info['plot_initial_values']:
        evolution = ramsey_fringe(1./info['fit_init_period']['s'],info['fit_init_T2']['s'],fit_init_phase,fit_init_contrast,0,detailed_times - offset_time)
    else:
        evolution = ramsey_fringe(frequency(),T2(),phase(),contrast(),offset(),detailed_times - offset_time)            
    plot_fit_label = 'fit with T2 = {:.2f} ms and f = {:.1f} kHz'.format(T2()*10**6,10**-3 * frequency())
    plot_data_label = 'measured data'
    
else: print 'ERROR: type {} not recognized'.format(info['plot_type'])

#make plot
fig = pyplot.figure()
pyplot.plot(detailed_times*10**6 , evolution,  'b', label = plot_fit_label,linewidth=2)
pyplot.plot(times*10**6, prob, 'o', label = plot_data_label,color='red')
pyplot.hold(True)
pyplot.legend()
pyplot.title(info['title'])
pyplot.xlabel('time (us)')
pyplot.ylabel('D state occupation probability')
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()