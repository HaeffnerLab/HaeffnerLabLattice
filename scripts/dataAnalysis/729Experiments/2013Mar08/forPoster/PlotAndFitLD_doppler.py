import labrad
import matplotlib
matplotlib.use('Qt4Agg')
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


# DRIFTED OUT
#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping',date]
flop_files = ['1446_43','1443_38','1449_49','1452_55','1456_01','1459_08','1502_13','1505_19']

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse',date]
dephase_files = ['1445_21','1448_26','1451_32','1454_38','1457_44','1500_51','1503_57']


flop_numbers = range(len(flop_files))
dephase_numbers = range(len(dephase_files))

#parameters and initial guesses for fit
sideband = 1.0
trap_frequency = U.WithUnit(2.85,'MHz')
amax=2000.0
f_Rabi_init = U.WithUnit(82.2,'kHz')
nb_init = 3.0
delta_init = U.WithUnit(4.0,'Hz')
fit_range_min=U.WithUnit(0.0,'us')
fit_range_max=U.WithUnit(250.0,'us')
delta_fluc_init=U.WithUnit(5,'Hz')
dephasing_time_offset=U.WithUnit(0.0,'us')

#SET PARAMETERS
nb = Parameter(nb_init)
f_Rabi = Parameter(f_Rabi_init['Hz'])
delta = Parameter(delta_init['Hz'])
delta_fluc=Parameter(delta_fluc_init['Hz'])
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

#fit to theory
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
pyplot.plot(deph_x_axis*10**6,deph_fit_y_axis,'b--',linewidth=2.0)

flop_fit_y_axis = evo.state_evolution_fluc(flop_x_axis, nb(), f_Rabi(), delta(),delta_fluc())
pyplot.plot(flop_x_axis*10**6,flop_fit_y_axis,'r-',linewidth=2.0)
m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
print 'Flop maximum at {:.2f} us'.format(flop_x_axis[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(flop_x_axis[m]/2.0*10**6)

#pyplot(sb.x,sb.flop)

pyplot.plot(flop_x_axis*10**6,flop_y_axis, 'ro',markersize = 8)
pyplot.plot(deph_x_axis*10**6,deph_y_axis, 'bs',markersize = 8)
#pyplot.xlabel('t in us')
pyplot.ylim((0,1))
#pyplot.ylabel('Population in the D-5/2 state')# + {0:.0f} kHz'.format(ymin))
#pyplot.legend()
#pyplot.text(xmax*0.70*10**6,0.83, 'nbar = {:.2f}'.format(nb()))
#pyplot.text(xmax*0.70*10**6,0.88, 'Rabi Frequency f = {:.2f} kHz'.format(f_Rabi()*10**(-3)))
#pyplot.title('Local detection on the first blue sideband')
pyplot.tick_params(axis='x', labelsize=26)
pyplot.tick_params(axis='y', labelsize=26)
pyplot.show()
