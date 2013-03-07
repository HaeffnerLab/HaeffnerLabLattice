"""
Fitter for Carrier and Sideband Rabi Flopping or Ramsey Fringes.####
"""
import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguer
from scipy import optimize
import matplotlib 
matplotlib.use('Qt4Agg')
from matplotlib import pyplot, pylab
import labrad
from labrad import units as U
import timeevolution as te

# PROVIDE INFO FOR PLOTS
        #'dataset' has three levels: 
        #    1st level: plots which need to be averaged (NEED TO SHARE SAME TIME AXIS)
        #    2nd level: sets to be joined to one plot (CONSECUTIVE TIME AXES)
        #    3rd level: Dates and Filenames of the parts
        
info = {'plot_type':'rabi_flop',
        'title':'Rabi-Flop', 
        'sideband':1,
        'offset_time': U.WithUnit(600.0,'ns'),
        'trap_frequency': U.WithUnit(2.84736, 'MHz'), #ENTER WITHOUT 2Pi FACTOR (UNLIKE THEORY PREDICTION)
        'nmax':1000,
        'fit_until':U.WithUnit(100,'us'),
        'fit_from':U.WithUnit(1,'us'),
        'folder':'RabiFlopping',
        #'datasets':[[['2013Feb05','1137_00'],['2013Feb05','1138_55']]],
        #'datasets':[[['2013Feb05','1433_43']],[['2013Feb05','1431_49']],[['2013Feb05','1435_40']]],
        'datasets':[[['2013Mar06','0033_00']]],#0034_31
        'fit_init_nbar':8,
        'fit_init_RabiPiTime':U.WithUnit(75,'us'),
        'fixed_fRabi':U.WithUnit(41.4,'kHz'),
        'plot_initial_values':False}
#info = {
#        'plot_type':'ramsey_fringe',
#        'title':'Ramsey Fringes', 
#        'fit_from':U.WithUnit(3,'us'),
##        'fit_until':U.WithUnit(36,'us'),
#        'folder':'RamseyDephaseScanDuration',
#        #'datasets':[[['2013Jan17','1731_45'],['2013Jan17','1733_00']]],
#        #'datasets':[[['2012Dec20','2105_00']]],
#        #'datasets':[[['2012Dec20','2121_24'],['2012Dec20','2123_16']]],
#        'datasets':[[['2013Mar06','0043_36']]],
#        'fit_init_period':U.WithUnit(40,'us'),
#        'fit_init_T2':U.WithUnit(2000,'us'),
#        'fit_init_phase':0,
#        'fit_init_contrast':1.2,
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
        dv.cd( ['','Experiments',folder,date,datasetName] )
        dv.open(1)  
        addto_times,addto_prob = dv.get().asarray.transpose()
        times=np.concatenate((times,addto_times))
        prob=np.concatenate((prob,addto_prob))
    prob_list.append(prob)
#print times
times=times*10**-6
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
fit_times = detailed_times - offset_time

# Find out what data and fit
if info['plot_type']=='rabi_flop':
    nbar = Parameter(info['fit_init_nbar'])
    if 'sideband' in info: sideband_order=info['sideband'] 
    else: sideband_order=0
    if 'nmax' in info: nmax=info['nmax']
    else: nmax=1000
    trap_frequency = info['trap_frequency']
    flop = te.time_evolution(nmax=nmax,trap_frequency = trap_frequency, sideband_order = sideband_order)
    fit_init_fRabi=.5/(info['fit_init_RabiPiTime']['s']*(flop.eta*np.sqrt(info['fit_init_nbar']))**sideband_order)
    if 'fixed_fRabi' in info: fit_init_fRabi=info['fixed_fRabi']['Hz']
    f_Rabi = Parameter(fit_init_fRabi)
    def f(t):
        evolution = flop.state_evolution(nbar(), f_Rabi(), t)
        return evolution
    def f_fix(t):
        evolution = flop.state_evolution(nbar(), fit_init_fRabi, t)
        return evolution
    if 'fixed_fRabi' in info:
        p,success = fit(f_fix, [nbar], y = prob[fitting_region], x = times[fitting_region] - offset_time)
    else:
        p,success = fit(f, [nbar,f_Rabi], y = prob[fitting_region], x = times[fitting_region] - offset_time)
        print 'fit for f_Rabi is ', f_Rabi()
    print 'fit for nbar is', nbar()
    if 'plot_initial_values' in info and info['plot_initial_values']:
        evolution = flop.state_evolution( info['fit_init_nbar'], fit_init_fRabi, detailed_times - offset_time )
    else:
        evolution = flop.state_evolution( nbar(),f_Rabi(), fit_times )
    pi_time_arg = pylab.unravel_index(np.array(evolution).argmax(),np.array(evolution).shape)
    pi_time = fit_times[pi_time_arg]
    print 'Rabi Pi Time is {} us'.format((pi_time+offset_time)*10**6)
    print 'Rabi Pi/2 Time is {} us'.format((pi_time)/2.0*10**6+offset_time*10**6)
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
    print 'period is {} us'.format(1./frequency()*10**6)
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