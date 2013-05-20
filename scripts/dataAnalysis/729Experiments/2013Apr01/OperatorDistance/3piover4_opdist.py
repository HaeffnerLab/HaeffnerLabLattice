import labrad
import matplotlib

from matplotlib import pyplot, pylab
import numpy as np
from scipy import optimize
#from scipy.stats import chi2
import timeevolution as tp
from labrad import units as U

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

#get access to servers
cxn = labrad.connect('192.168.169.197', password = 'lab')
dv = cxn.data_vault

# set to right date
date1 = '2013Mar15'
date2 = '2013Mar16'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping']
flop_files = [[date1,'2310_22'],[date1,'2317_38'],[date1,'2323_28'],[date1,'2338_10'],[date1,'2345_26'],[date1,'2351_16'],[date1,'2358_32'],[date2,'0005_54'],[date2,'0011_35']]

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse']
dephase_files = [[date1,'2313_32'],[date1,'2320_57'],[date1,'2328_13'],[date1,'2335_30'],[date1,'2341_20'],[date1,'2348_36'],[date1,'2356_01'],[date2,'0001_51'],[date2,'0009_04']]


flop_numbers = range(len(flop_files))
dephase_numbers = range(len(dephase_files))

#parameters and initial guesses for fit
sideband = 1.0
trap_frequency = U.WithUnit(2.79,'MHz')
amax=1000.0
f_Rabi_init = U.WithUnit(85.0,'kHz')
nb_init = 0.1
delta_init = U.WithUnit(1000.0,'Hz')
fit_range_min=U.WithUnit(0.0,'us')
fit_range_max=U.WithUnit(400.0,'us')
delta_fluc_init=U.WithUnit(1000.0,'Hz')
dephasing_time_offset=U.WithUnit(0,'us')

#SET PARAMETERS
nb = Parameter(nb_init)
f_Rabi = Parameter(f_Rabi_init['Hz'])
delta = Parameter(delta_init['Hz'])
delta_fluc=Parameter(delta_fluc_init['Hz'])
#which to fit?
fit_params = [nb,f_Rabi,delta,delta_fluc]

# take list of Rabi flops and average
dv.cd(flop_directory)
flop_y_axis_list=[]
for i in flop_numbers:
    dv.cd(flop_files[i])
    dv.open(1)
    data = dv.get().asarray
    flop_y_axis_list.append(data[:,1])
    dv.cd(2)

flop_y_axis = np.sum(flop_y_axis_list,axis=0)/np.float32(len(flop_files))
flop_x_axis=data[:,0]*10**(-6)

xmax=max(flop_x_axis)

# take list of evolutions with differnet phases and average --> dephasing!
dv.cd(dephase_directory)
deph_y_axis_list=[]
for i in dephase_numbers:
    dv.cd(dephase_files[i])
    dv.open(1)
    data = dv.get().asarray
    deph_y_axis_list.append(data[:,1])
    dv.cd(2)

deph_y_axis = np.sum(deph_y_axis_list,axis=0)/np.float32(len(dephase_files))
deph_x_axis=data[:,0]*10**(-6)+dephasing_time_offset['s']
t0 = deph_x_axis.min()+dephasing_time_offset['s']

#fit Rabi Flops to theory
evo=tp.time_evolution(trap_frequency, sideband,nmax = 1000)
def f(x):
    evolution = evo.state_evolution_fluc(x,nb(),f_Rabi(),delta(),delta_fluc())
    return evolution

fitting_region = np.where((flop_x_axis >= fit_range_min['s'])&(flop_x_axis <= fit_range_max['s']))
print 'Fitting...'
p,success = fit(f, fit_params, y = flop_y_axis[fitting_region], x = flop_x_axis[fitting_region])
print 'Fitting DONE.'

figure = pyplot.figure()

print "nbar = {}".format(nb())
print "Rabi Frequency = {} kHz".format(f_Rabi()*10**(-3))
print "The detuning is centered around {} kHz and spreads with a variance of {} kHz".format(delta()*10**-3,np.abs(delta_fluc())*10**-3)

## START FIT DEPHASING (still a hack)
##fit dephasing curve
#def f_deph(x):
#    evolution = evo.deph_evolution_fluc(x,t0,nb(),f_Rabi(),delta(),delta_fluc())
#    return evolution
#fit_range_max=U.WithUnit(300.0,'us')
#fitting_region = np.where((deph_x_axis >= fit_range_min['s'])&(deph_x_axis <= fit_range_max['s']))
#print 'Fitting...'
#p,success = fit(f_deph, [nb,f_Rabi,delta,delta_fluc], y = deph_y_axis[fitting_region], x = deph_x_axis[fitting_region])
#print 'Fitting DONE.'
#
#print "nbar = {}".format(nb())
#print "Rabi Frequency = {} kHz".format(f_Rabi()*10**(-3))
#print "The detuning is centered around {} kHz and spreads with a variance of {} kHz".format(delta()*10**-3,np.abs(delta_fluc())*10**-3)
#
#flop_fit_y_axis = evo.state_evolution_fluc(flop_x_axis, nb(), f_Rabi(), delta(),delta_fluc())
#m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
#print 'Flop maximum at {:.2f} us'.format(flop_x_axis[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(flop_x_axis[m]/2.0*10**6)
#
deph_fit_y_axis = evo.deph_evolution_fluc(deph_x_axis, t0,nb(),f_Rabi(),delta(),delta_fluc())
#pyplot.plot(deph_x_axis*10**6,deph_fit_y_axis,'b--')

flop_fit_y_axis = evo.state_evolution_fluc(flop_x_axis, nb(), f_Rabi(), delta(),delta_fluc())
#pyplot.plot(flop_x_axis*10**6,flop_fit_y_axis,'r-')
m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
print 'Flop maximum at {:.2f} us'.format(flop_x_axis[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(flop_x_axis[m]/2.0*10**6)
print 'Actual t0 = {}'.format(t0)

#pyplot.plot(flop_x_axis*10**6,flop_y_axis, 'ro')
#pyplot.plot(deph_x_axis*10**6,deph_y_axis, 'bs')
pyplot.xlabel('t in us')
pyplot.ylim((0,0.25))
pyplot.ylabel('Population in the D-5/2 state')
#pyplot.legend()
subseq_evolution=np.where(flop_x_axis>=t0)
nicer_resolution = np.linspace(t0,flop_x_axis.max(),1000)
deph_fit_y_axis = evo.deph_evolution_fluc(nicer_resolution, t0,nb(),f_Rabi(),delta(),delta_fluc())
flop_fit_y_axis = evo.state_evolution_fluc(nicer_resolution, nb(), f_Rabi(), delta(),delta_fluc())

flop_interpolated = np.interp(deph_x_axis,flop_x_axis[subseq_evolution],flop_y_axis[subseq_evolution])

exp_diff = 2.0*np.abs(flop_interpolated-deph_y_axis)**2
theo_diff = 2.0*np.abs(flop_fit_y_axis-deph_fit_y_axis)**2
e_flop = np.sqrt(flop_interpolated*(1-flop_interpolated)/(100.0*len(flop_files)))
e_deph = np.sqrt(deph_y_axis*(1-deph_y_axis)/(100.0*len(dephase_files)))
exp_diff_errs = np.sqrt(8.0*exp_diff*(e_flop**2+e_deph**2))

average_where=np.where((deph_x_axis-t0)*f_Rabi()<=24.27)
time_average=np.average(exp_diff[average_where])
print 'average distance = {}'.format(time_average)
print '[{},{}]'.format(f_Rabi()*t0,time_average)
print 'mean error = {}'.format(1.0/len(exp_diff[average_where])*np.sqrt(np.sum(exp_diff_errs**2)))
print 'nbar = {}'.format(nb())

pyplot.plot(f_Rabi()*(deph_x_axis-t0),exp_diff,'ko')
pyplot.plot(f_Rabi()*(nicer_resolution-t0),theo_diff,'k-')
pyplot.errorbar(f_Rabi()*(deph_x_axis-t0), exp_diff, exp_diff_errs, xerr = 0, fmt='ko')
pyplot.show()