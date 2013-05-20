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
date = '2013Mar08'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping',date]
flop_files = ['2349_55','2342_02','2314_37','2243_04','2250_58','2306_45','2334_09','2258_52','2357_48']

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse',date]
dephase_files = ['2255_02','2318_41','2346_06','2302_56','2247_09','2330_20','2338_12','2353_59','2310_49']


flop_numbers = range(len(flop_files))
dephase_numbers = range(len(dephase_files))

#parameters and initial guesses for fit
sideband = 1.0
trap_frequency = U.WithUnit(2.85,'MHz')
amax=1000.0
f_Rabi_init = U.WithUnit(120.0,'kHz')
nb_init = 0.3
delta_init = U.WithUnit(1000.0,'Hz')
fit_range_min=U.WithUnit(0.0,'us')
fit_range_max=U.WithUnit(75.0,'us')
delta_fluc_init=U.WithUnit(100.0,'Hz')
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
    dv.cd(1)

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
    dv.cd(1)

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

pyplot.plot(flop_x_axis*10**6,flop_y_axis, 'ro')
pyplot.plot(deph_x_axis*10**6,deph_y_axis, 'bs')
pyplot.xlabel('t in us')
pyplot.ylim((0,1))
pyplot.ylabel('Population in the D-5/2 state')
#pyplot.legend()
pyplot.text(xmax*0.70*10**6,0.83, 'nbar = {:.2f}'.format(nb()))
pyplot.text(xmax*0.70*10**6,0.88, 'Rabi Frequency f = {:.2f} kHz'.format(f_Rabi()*10**(-3)))
pyplot.title('Local detection on the first blue sideband')
pyplot.show()
