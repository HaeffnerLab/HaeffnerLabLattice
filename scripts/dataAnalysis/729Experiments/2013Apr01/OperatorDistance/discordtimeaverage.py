import matplotlib

from matplotlib import pyplot
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

#Times (Pi/4,Pi/2,3Pi/4,Pi,3Pi/2)
times = [0,2.82713003685,5.27355837955,8.8792654291,11.2252501165,17.2867104081]
averages = [0,0.0497868898282,0.154861025572,0.0655491449449,0.0163914766524,0.144347495801]
errors = [0,0.00261032973942,0.00409218262306,0.00341273149921,0.00176529911012,0.00525374485925]

nbars =[0.185631982212,0.198141427699,0.123993486485,0.167394549013,0.217396568974]

nbar = np.average(nbars)

#fit Rabi Flops to theory
evo=tp.time_evolution(trap_frequency, sideband,nmax = 1000)
def f(x):
    evolution = evo.discord_fluc(x,nb(),f_Rabi(),delta(),delta_fluc())
    return evolution

#fitting_region = np.where((flop_x_axis >= fit_range_min['s'])&(flop_x_axis <= fit_range_max['s']))
#print 'Fitting...'
#p,success = fit(f, fit_params, y = flop_y_axis[fitting_region], x = flop_x_axis[fitting_region])
#print 'Fitting DONE.'

figure = pyplot.figure()
#
#print "nbar = {}".format(nb())
#print "Rabi Frequency = {} kHz".format(f_Rabi()*10**(-3))
#print "The detuning is centered around {} kHz and spreads with a variance of {} kHz".format(delta()*10**-3,np.abs(delta_fluc())*10**-3)

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
#deph_fit_y_axis = evo.deph_evolution_fluc(deph_x_axis, t0,nb(),f_Rabi(),delta(),delta_fluc())
#pyplot.plot(deph_x_axis*10**6,deph_fit_y_axis,'b--')

#flop_fit_y_axis = evo.state_evolution_fluc(flop_x_axis, nb(), f_Rabi(), delta(),delta_fluc())
#pyplot.plot(flop_x_axis*10**6,flop_fit_y_axis,'r-')
#m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
#print 'Flop maximum at {:.2f} us'.format(flop_x_axis[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(flop_x_axis[m]/2.0*10**6)
#print 'Actual t0 = {}'.format(t0)

#pyplot.plot(flop_x_axis*10**6,flop_y_axis, 'ro')
#pyplot.plot(deph_x_axis*10**6,deph_y_axis, 'bs')
fake_f = 100000

timescale = evo.effective_rabi_coupling(nb())*2.0*np.pi
label = r'$\Omega t$'

pyplot.xlabel(r'Excitation time '+label,fontsize=44)
pyplot.ylim((0,1))
#pyplot.ylabel('Operator Distance')
#pyplot.legend()

fake_times = np.linspace(np.array(times).min()/(fake_f),np.array(times).max()/(fake_f),1000)
discord = evo.discord(fake_times, nbar, fake_f)
flop = evo.state_evolution(fake_times, nbar, fake_f)

pyplot.plot(np.array(times)*timescale,2.0*np.array(averages),'ko',label='Time-Averaged Qubit Distance')
pyplot.plot(fake_times*fake_f*timescale,discord,'k-',label='Discord between Qubit and Motion')
pyplot.plot(fake_times*fake_f*timescale,flop,'b-',label='Blue Sideband Rabi Flop, nbar = {:.2f}'.format(nbar))
pyplot.errorbar(np.array(times)*timescale, 2.0*np.array(averages), 2.0*np.array(errors), xerr=0, fmt='ko')

pyplot.legend(loc=2,prop={'size':25})
pyplot.title('Time-Averaged Distance to Assess Quantum Discord',fontsize=50)
pyplot.tick_params(axis='x', labelsize=40)
pyplot.tick_params(axis='y', labelsize=40)
pyplot.xticks([np.pi/4.0,3.0*np.pi/4.0,np.pi/2.0,np.pi,5.0*np.pi/4.0,3.0*np.pi/2.0],[r'$\frac{\pi}{4}$',r'$\frac{3\pi}{4}$',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$'])
pyplot.show()