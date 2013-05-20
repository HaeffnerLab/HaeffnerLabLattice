import labrad
import matplotlib

from matplotlib import pyplot, pylab
import numpy as np
from scipy import optimize
#from scipy.stats import chi2
import timeevolution as tp
from labrad import units as U

# set to right date
date = '2013Apr02'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping',date]
blue_file='1926_23'
red_file='1923_51'

size=.8

#parameters and initial guesses for fit
sideband = 1.0
amax=2000.0
f_Rabi_init = U.WithUnit(85.0,'kHz')
nb_init = 2.89883943944
delta_init = U.WithUnit(1000.0,'Hz')
fit_range_min=U.WithUnit(0.0,'us')
fit_range_max=U.WithUnit(100.0,'us')
delta_fluc_init=U.WithUnit(100.0,'Hz')
dephasing_time_offset=U.WithUnit(0,'us')

#actual script starts here
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

#get trap frequency
dv.cd(flop_directory)
dv.cd(blue_file)
dv.open(1)
sideband_selection = dv.get_parameter('RabiFlopping.sideband_selection')
sb = np.array(sideband_selection)
trap_frequencies = ['TrapFrequencies.radial_frequency_1','TrapFrequencies.radial_frequency_2','TrapFrequencies.axial_frequency','TrapFrequencies.rf_drive_frequency']
trap_frequency = dv.get_parameter(str(np.array(trap_frequencies)[sb.nonzero()][0]))            
print 'trap frequency is {}'.format(trap_frequency)

#SET PARAMETERS
nb = Parameter(nb_init)
f_Rabi = Parameter(f_Rabi_init['Hz'])
delta = Parameter(delta_init['Hz'])
delta_fluc=Parameter(delta_fluc_init['Hz'])
#which to fit?
fit_params = [nb,f_Rabi,delta,delta_fluc]

# take Rabi flops
data = dv.get().asarray
blue_flop_y_axis = data[:,1]
blue_flop_x_axis = data[:,0]*10**(-6)
dv.cd(1)

dv.cd(red_file)
dv.open(1)
data = dv.get().asarray
red_flop_y_axis = data[:,1]
red_flop_x_axis = data[:,0]*10**(-6)

#fit Rabi Flops to theory
blue_evo=tp.time_evolution(trap_frequency, sideband,nmax = amax)
def blue_f(x):
    evolution = blue_evo.state_evolution_fluc(x,nb(),f_Rabi(),delta(),delta_fluc())
    return evolution

red_evo=tp.time_evolution(trap_frequency, -sideband,nmax = amax)
def red_f(x):
    evolution = red_evo.state_evolution_fluc(x,nb(),f_Rabi(),delta(),delta_fluc())
    return evolution


blue_xmax=max(blue_flop_x_axis)
red_xmax=max(red_flop_x_axis)
figure = pyplot.figure()

#FIT BLUE

fitting_region = np.where((blue_flop_x_axis >= fit_range_min['s'])&(blue_flop_x_axis <= fit_range_max['s']))
print 'Fitting blue...'
p,success = fit(blue_f, fit_params, y = blue_flop_y_axis[fitting_region], x = blue_flop_x_axis[fitting_region])
print 'Fitting DONE.'

print "nbar = {}".format(nb())
print "Rabi Frequency = {} kHz".format(f_Rabi()*10**(-3))
print "The detuning is ({:.2f} +- {:.2f}) kHz".format(delta()*10**-3,np.abs(delta_fluc())*10**-3)

blue_nicer_resolution = np.linspace(0,blue_flop_x_axis.max(),1000)
blue_flop_fit_y_axis = blue_evo.state_evolution_fluc(blue_nicer_resolution, nb(), f_Rabi(), delta(),delta_fluc())

m=pylab.unravel_index(np.array(blue_flop_fit_y_axis).argmax(), np.array(blue_flop_fit_y_axis).shape)
print 'blue sideband highest peak value = {} at {}'.format(np.array(blue_flop_fit_y_axis).max(),10**6*blue_nicer_resolution[m])
blue_max = np.array(blue_flop_fit_y_axis).max()

blue_fit_nbar = nb()

fit_params = [nb,delta,delta_fluc]
#FIT RED
fitting_region = np.where((red_flop_x_axis >= fit_range_min['s'])&(red_flop_x_axis <= fit_range_max['s']))
print 'Fitting red...'
p,success = fit(red_f, fit_params, y = red_flop_y_axis[fitting_region], x = red_flop_x_axis[fitting_region])
print 'Fitting DONE.'

print "red nbar = {}".format(nb())
print "Rabi Frequency = {} kHz".format(f_Rabi()*10**(-3))
print "The detuning is ({:.2f} +- {:.2f}) kHz".format(delta()*10**-3,np.abs(delta_fluc())*10**-3)

red_nicer_resolution = np.linspace(0,red_flop_x_axis.max(),1000)
red_flop_fit_y_axis = red_evo.state_evolution_fluc(red_nicer_resolution, nb(), f_Rabi(), delta(),delta_fluc())

mred=pylab.unravel_index(np.array(red_flop_fit_y_axis).argmax(), np.array(red_flop_fit_y_axis).shape)
print 'red sideband highest peak value = {} at {}'.format(np.array(red_flop_fit_y_axis).max(),10**6*red_nicer_resolution[mred])
red_max = red_flop_fit_y_axis[m]

red_fit_nbar = nb()

average_nbar = 0.5*(blue_fit_nbar+red_fit_nbar)
r = red_max/blue_max
ratio_nbar = r/(1-r) 
print 'nbar = {}'.format(ratio_nbar)

pyplot.plot(blue_nicer_resolution*10**6,blue_flop_fit_y_axis,'b-')
yerrflop = np.sqrt((1-blue_flop_y_axis)*blue_flop_y_axis/(100.0))
pyplot.errorbar(blue_flop_x_axis*10**6, blue_flop_y_axis, yerrflop, xerr = 0, fmt='bo')

pyplot.xlabel(r'Evolution time in $\mu s$',fontsize=size*22)
pyplot.ylim((0,1))
pyplot.ylabel('Local Hilbert-Schmidt Distance',fontsize=size*22)
#pyplot.legend()

pyplot.plot(red_nicer_resolution*10**6,red_flop_fit_y_axis,'r-')
yerrflop = np.sqrt((1-red_flop_y_axis)*red_flop_y_axis/(100.0))
pyplot.errorbar(red_flop_x_axis*10**6, red_flop_y_axis, yerrflop, xerr = 0, fmt='ro')

pyplot.text(blue_xmax*0.70*10**6,0.83, 'average fit nbar = {:.2f}'.format(average_nbar))
pyplot.text(blue_xmax*0.70*10**6,0.80, 'ratio nbar = {:.2f}'.format(ratio_nbar))
pyplot.tick_params(axis='x', labelsize=size*20)
pyplot.tick_params(axis='y', labelsize=size*20)

pyplot.show()