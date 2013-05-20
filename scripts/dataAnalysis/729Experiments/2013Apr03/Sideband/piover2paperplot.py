import labrad
import matplotlib

from matplotlib import pyplot, pylab
import numpy as np
from scipy import optimize
#from scipy.stats import chi2
import timeevolution as tp
from labrad import units as U

# set to right date
date = '2013Mar15'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping',date]
flop_files = ['1909_27','1914_49','1919_51','1924_54','1930_12','1935_15','1940_18','1945_21','1950_23','1955_44']
parameter_file = '1902_48'
red_file='1906_46'

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse',date]
dephase_files = ['1912_14','1917_27','1922_39','1927_41','1933_00','1938_02','1943_05','1948_08','1953_11','1958_22']

#Plotting and averaging parameter
ymax = 0.5
size = 1.3
average_until = 23.9
realtime = True
dephasing_time_string = r'$\frac{\pi}{2}$'

#parameters and initial guesses for fit
sideband = 1.0
amax=2000.0
f_Rabi_init = U.WithUnit(85.0,'kHz')
nb_init = 0.2
#nb_init = get_nbar(flop_directory, parameter_file, red_file, fit_until=U.WithUnit(250,'us'), show=True)
delta_init = U.WithUnit(1000.0,'Hz')
fit_range_min=U.WithUnit(0.0,'us')
fit_range_max=U.WithUnit(350.0,'us')
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


flop_numbers = range(len(flop_files))
dephase_numbers = range(len(dephase_files))

#get access to servers
cxn = labrad.connect('192.168.169.197', password = 'lab')
dv = cxn.data_vault

#get trap frequency
dv.cd(flop_directory)
dv.cd(parameter_file)
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
evo=tp.time_evolution(trap_frequency, sideband,nmax = amax)
def f(x):
    evolution = evo.state_evolution_fluc(x,nb(),f_Rabi(),delta(),delta_fluc())
    return evolution

fitting_region = np.where((flop_x_axis >= fit_range_min['s'])&(flop_x_axis <= fit_range_max['s']))
print 'Fitting...'
p,success = fit(f, fit_params, y = flop_y_axis[fitting_region], x = flop_x_axis[fitting_region])
print 'Fitting DONE.'

figure = pyplot.figure(figsize=(15,7))
figure.subplots_adjust(left=0.08, right=0.98, bottom=0.13, top=0.95)

#print "nbar = {}".format(nb())
#print "Rabi Frequency = {} kHz".format(f_Rabi()*10**(-3))
print "The detuning is ({:.2f} +- {:.2f}) kHz".format(delta()*10**-3,np.abs(delta_fluc())*10**-3)

deph_fit_y_axis = evo.deph_evolution_fluc(deph_x_axis, t0,nb(),f_Rabi(),delta(),delta_fluc())
#pyplot.plot(deph_x_axis*10**6,deph_fit_y_axis,'b--')

flop_fit_y_axis = evo.state_evolution_fluc(flop_x_axis, nb(), f_Rabi(), delta(),delta_fluc())
#pyplot.plot(flop_x_axis*10**6,flop_fit_y_axis,'r-')
m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
#print 'Flop maximum at {:.2f} us'.format(flop_x_axis[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(flop_x_axis[m]/2.0*10**6)
#print 'Actual t0 = {}'.format(t0)

if realtime:
    timescale = 10**6
    label = r'in $\mu s$'
else:
    timescale = evo.effective_rabi_coupling(nb())*f_Rabi()*2.0*np.pi
    label = r'$\frac{\Omega t}{2\pi}$'

detail_flop = np.linspace(flop_x_axis.min(),flop_x_axis.max(),1000)
detail_deph = np.linspace(deph_x_axis.min(),deph_x_axis.max(),1000)

deph_fit_y_axis = evo.deph_evolution_fluc(detail_deph, t0,nb(),f_Rabi(),delta(),delta_fluc())
pyplot.plot(detail_deph*timescale-t0*timescale,deph_fit_y_axis,'b--')

flop_fit_y_axis = evo.state_evolution_fluc(detail_flop, nb(), f_Rabi(), delta(),delta_fluc())

#m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
#print 'Flop maximum at {:.2f} us'.format(detail_flop[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(detail_flop[m]/2.0*10**6)
#print 'Actual t0 = {}'.format(t0)

before=np.where(flop_x_axis<t0)
after=np.where(flop_x_axis>=t0)

#pyplot.plot(np.array(flop_x_axis[before])*timescale,flop_y_axis[before], 'ro')

yerrflop = np.sqrt((1-flop_y_axis)*flop_y_axis/(100.0*len(flop_files)))
yerrdeph = np.sqrt((1-deph_y_axis)*deph_y_axis/(100.0*len(dephase_files)))

for where in [before,after]:
    if where == before:
        plotformat='ko'
        format_theo='k-'
        mfc='k'
        where_theo=np.where(detail_flop<t0)
    else:
        plotformat='ro'
        format_theo='r-'
        mfc='r'
        where_theo=np.where(detail_flop>=t0)
    pyplot.errorbar(np.array(flop_x_axis[where])*timescale-t0*timescale, flop_y_axis[where], yerr=yerrflop[where], xerr=0,fmt=plotformat,mew=2,capsize=3,ms=5,mfc=mfc,mec=mfc)
    pyplot.plot(detail_flop[where_theo]*timescale-t0*timescale,flop_fit_y_axis[where_theo],format_theo,lw=2)
    
pyplot.errorbar(np.array(deph_x_axis)*timescale-t0*timescale, deph_y_axis, yerr=yerrdeph, xerr=0,fmt='bo',mew=2,capsize=3,ms=5,mfc='b',mec='b')

pyplot.bar([-t0*timescale], [1], t0*timescale, 0,label=None,color='#D0D0D0')
pyplot.xlabel('Excitation Duration '+label, fontsize = size*22)
pyplot.ylim((0,1))
#pyplot.xlim((-t0*timescale,(flop_x_axis.max()-t0)*timescale))
pyplot.xlim((-t0*timescale,280))
pyplot.ylabel(r'Population in the $\left|1\right\rangle$ state', fontsize = size*22)
pyplot.grid(True,'major')
#pyplot.legend()
#pyplot.text(xmax*0.35*timescale,0.80, 'nbar = {:.2f}'.format(nb()), fontsize = size*22)
#pyplot.text(xmax*0.35*timescale,0.88, 'Rabi Frequency {:.1f} kHz'.format(f_Rabi()*10**(-3)), fontsize = size*22)
#pyplot.title('Local detection on the first blue sideband', fontsize = size*30)
pyplot.tick_params(axis='x', labelsize=size*20)
pyplot.tick_params(axis='y', labelsize=size*20)
pyplot.show()