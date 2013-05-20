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
date = '2013Mar15'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping',date]
flop_files = ['1909_27','1914_49','1919_51','1924_54','1930_12','1935_15','1940_18','1945_21','1950_23','1955_44']

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse',date]
dephase_files = ['1912_14','1917_27','1922_39','1927_41','1933_00','1938_02','1943_05','1948_08','1953_11','1958_22']


flop_numbers = range(len(flop_files))
dephase_numbers = range(len(dephase_files))

#parameters and initial guesses for fit
sideband = 1.0
trap_frequency = U.WithUnit(2.8,'MHz')
amax=1000.0
f_Rabi_init = U.WithUnit(85.0,'kHz')
nb_init = 0.1
delta_init = U.WithUnit(1000.0,'Hz')
fit_range_min=U.WithUnit(0.0,'us')
fit_range_max=U.WithUnit(350.0,'us')
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
realtime = True

if realtime:
    timescale = 10**6
    label = r'in $\mu s$'
else:
    timescale = evo.effective_rabi_coupling(nb())*f_Rabi()*2.0*np.pi
    label = r'$\frac{\Omega t}{2\pi}$'

detail_flop = np.linspace(flop_x_axis.min(),flop_x_axis.max(),1000)
detail_deph = np.linspace(deph_x_axis.min(),deph_x_axis.max(),1000)

deph_fit_y_axis = evo.deph_evolution_fluc(detail_deph, t0,nb(),f_Rabi(),delta(),delta_fluc())
pyplot.plot(detail_deph*timescale,deph_fit_y_axis,'b--')

flop_fit_y_axis = evo.state_evolution_fluc(detail_flop, nb(), f_Rabi(), delta(),delta_fluc())
pyplot.plot(detail_flop*timescale,flop_fit_y_axis,'r-')

m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
print 'Flop maximum at {:.2f} us'.format(detail_flop[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(detail_flop[m]/2.0*10**6)
print 'Actual t0 = {}'.format(t0)

pyplot.plot(np.array(flop_x_axis)*timescale,flop_y_axis, 'ro')

yerrflop = np.sqrt((1-flop_y_axis)*flop_y_axis/(100.0*len(flop_files)))
pyplot.errorbar(np.array(flop_x_axis)*timescale, flop_y_axis, yerr=yerrflop, xerr=0,fmt='ro')
yerrdeph = np.sqrt((1-deph_y_axis)*deph_y_axis/(100.0*len(dephase_files)))
pyplot.errorbar(np.array(deph_x_axis)*timescale, deph_y_axis, yerr=yerrdeph, xerr=0,fmt='bo')
pyplot.plot(np.array(deph_x_axis)*timescale,deph_y_axis, 'bs')
pyplot.xlabel('Excitation Duration '+label, fontsize = 44)
pyplot.ylim((0,1))
pyplot.ylabel('Population in the D-5/2 state', fontsize = 44)
#pyplot.legend()
pyplot.text(xmax*0.6*timescale,0.80, 'nbar = {:.1f}'.format(nb()), fontsize = 44)
pyplot.text(xmax*0.6*timescale,0.88, 'Rabi Frequency {:.1f} kHz'.format(f_Rabi()*10**(-3)), fontsize = 44)
pyplot.title('Local detection on the first blue sideband', fontsize = 60)
pyplot.tick_params(axis='x', labelsize=40)
pyplot.tick_params(axis='y', labelsize=40)
pyplot.show()
