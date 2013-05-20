import labrad
import matplotlib

from matplotlib import pyplot, pylab
import numpy as np
from scipy import optimize
import timeevolution as tp
from labrad import units as U

# RETAKEN DATA, BAD HEATING RATE, HIGH NBAR
# set to right date
date = '2013Apr05'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping',date]
flop_files = ['1553_45','1600_26','1607_17','1615_25','1622_07','1630_15','1637_06','1653_10','1700_10']
parameter_file='1549_00'

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse',date]
dephase_files = ['1556_26','1604_43','1611_25','1619_33','1626_15','1634_23','1641_14','1650_36','1657_36']


## OLDER DATA, GOOD NBAR AND HEATING RATE BUT SOME SHIFT IN DEPHASING
#date = '2013Mar15'
#
##provide list of Rabi flops - all need to have same x-axis
#flop_directory = ['','Experiments','RabiFlopping',date]
#flop_files = ['2033_35','2038_57','2044_27','2056_46','2102_17','2107_39','2113_01','2118_31','2123_53']
#parameter_file='2018_52'
#
##provide list of evolutions with different phases - all need to have same x-axis
#dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse',date]
#dephase_files = ['2036_26','2041_48','2047_18','2052_40','2059_37','2104_59','2110_30','2115_52','2121_22']

#Plotting and averaging parameter
ymax = 0.25
size = 1
average_until = 23.9
realtime = True
dephasing_time_string = r'$\frac{\pi}{4}$'
folder = 'piover4'

#parameters and initial guesses for fit
sideband = 1.0
amax=2000.0
f_Rabi_init = U.WithUnit(102.0,'kHz')
nb_init = 0.5
delta_init = U.WithUnit(1000.0,'Hz')
fit_range_min=U.WithUnit(0.0,'us')
fit_range_max=U.WithUnit(245.0,'us')
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
        
def fit(function, parameters, y, yerr,x = None):
    if x is None: x = np.arange(y.shape[0])
    restrict_to = np.nonzero(yerr)
    y=y[restrict_to]
    x=x[restrict_to]
    yerr=yerr[restrict_to]
    def f(params,x):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return function(x)
    fitfunc = lambda p, x: f(p,x)
    errfunc = lambda p,x,y,err: (y - fitfunc(p,x))/err
    p = [param() for param in parameters]
    return optimize.leastsq(errfunc, p,args=(x,y,yerr),full_output=True)

#def chi_square(data,fit_for_data,data_errs,reduced = True, number_of_params=0):
#    if reduced:
#        dof = np.float32(len(data)-number_of_params)
#    else:
#        dof = 1.0
#    nonzero_region = np.nonzero(data_errs)
#    data_errs = np.ones_like(data)
#    dof = 1.0
#    chi_square = np.sum(((data[nonzero_region]-fit_for_data[nonzero_region])/data_errs[nonzero_region])**2,axis=0)/dof
#    return chi_square

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

#redo ninth point: skip one file
broken_point_list=[]
dv.cd(flop_directory)
for i in flop_numbers:
    dv.cd(flop_files[i])
    dv.open(1)
    if not flop_files[i]=='1700_10':
        point = dv.get().asarray[8,1]
        broken_point_list.append(point)
    dv.cd(1)
broken_point = np.average(broken_point_list)
flop_y_axis[8]=broken_point


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

eta = evo.eta

fitting_region = np.where((flop_x_axis >= fit_range_min['s'])&(flop_x_axis <= fit_range_max['s']))
flop_errors = np.sqrt(flop_y_axis*(1-flop_y_axis)/(100.0*len(flop_files)))
print 'Fitting...'
p,cov,infodict,mesg,success = fit(f, fit_params, y = flop_y_axis[fitting_region], yerr=flop_errors[fitting_region],x = flop_x_axis[fitting_region])
print 'Fitting DONE.'

#print "nbar = {}".format(nb())
#print "Rabi Frequency = {} kHz".format(f_Rabi()*10**(-3))
print "The detuning fluctuates around ({:.2f} with a spread of {:.2f}) kHz".format(delta()*10**-3,np.abs(delta_fluc())*10**-3)

deph_fit_y_axis = evo.deph_evolution_fluc(deph_x_axis, t0,nb(),f_Rabi(),delta(),delta_fluc())
#pyplot.plot(deph_x_axis*10**6,deph_fit_y_axis,'b--')

flop_fit_y_axis = evo.state_evolution_fluc(flop_x_axis, nb(), f_Rabi(), delta(),delta_fluc())

#red_chi2 = chi_square(flop_y_axis[fitting_region], flop_fit_y_axis[fitting_region], flop_errors[fitting_region], True,len(fit_params))
figure = pyplot.figure()

i=0
for par in fit_params:
    print 'P[{}] = {} +- {}'.format(i,par(),np.sqrt(cov[i][i]))
    i+=1
    
enb = np.sqrt(cov[0][0])
ef_Rabi = np.sqrt(cov[1][1])

#pyplot.plot(flop_x_axis*10**6,flop_fit_y_axis,'r-')
m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
#print 'Flop maximum at {:.2f} us'.format(flop_x_axis[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(flop_x_axis[m]/2.0*10**6)
#print 'Actual t0 = {}'.format(t0)
#print '2pi time {}'.format(flop_x_axis[m]*f_Rabi()*2.0)

#pyplot.plot(flop_x_axis*10**6,flop_y_axis, 'ro')
#pyplot.plot(deph_x_axis*10**6,deph_y_axis, 'bs')
pyplot.xlabel(r'Subsequent evolution time $\frac{\Omega t}{2\pi}$',fontsize=size*22)
pyplot.ylim((0,ymax))
pyplot.ylabel('Local Hilbert-Schmidt Distance',fontsize=size*22)
#pyplot.legend()

subseq_evolution=np.where(flop_x_axis>=t0)
nicer_resolution = np.linspace(t0,flop_x_axis.max(),1000)
deph_fit_y_axis = evo.deph_evolution_fluc(nicer_resolution, t0,nb(),f_Rabi(),delta(),delta_fluc())
flop_fit_y_axis = evo.state_evolution_fluc(nicer_resolution, nb(), f_Rabi(), delta(),delta_fluc())

flop_interpolated = np.interp(deph_x_axis,flop_x_axis[subseq_evolution],flop_y_axis[subseq_evolution])

exp_diff = 2.0*np.abs(flop_interpolated-deph_y_axis)**2
theo_diff = 2.0*np.abs(flop_fit_y_axis-deph_fit_y_axis)**2
e_flop = np.sqrt(flop_interpolated*(1-flop_interpolated)/(100.0*len(flop_files)))
e_flop[8] = np.sqrt(flop_y_axis[8]*(1-flop_y_axis[8])/(100.0*(len(flop_files)-1)))
e_deph = np.sqrt(deph_y_axis*(1-deph_y_axis)/(100.0*len(dephase_files)))
exp_diff_errs = np.sqrt(8.0*exp_diff*(e_flop**2+e_deph**2))

average_where=np.where((deph_x_axis-t0)*f_Rabi()<=average_until)
time_average=np.average(exp_diff[average_where])
#print 'parameters for time average: [t0,time_average,error,nbar,trap_frequency]'
#print '[{},{},{},{},{}]'.format(f_Rabi()*t0,time_average,1.0/len(exp_diff[average_where])*np.sqrt(np.sum(exp_diff_errs**2)),nb(),trap_frequency['MHz'])

print 'nbar = {:.2f}+-{:.2f}\nf_Rabi = {:.2f}+-{:.2f} kHz'.format(nb(),enb,10**-3*f_Rabi(),10**-3*ef_Rabi)

pyplot.plot(eta*f_Rabi()*(deph_x_axis-t0),exp_diff,'ko')
pyplot.plot(eta*f_Rabi()*(nicer_resolution-t0),theo_diff,'k-')
pyplot.errorbar(eta*f_Rabi()*(deph_x_axis-t0), exp_diff, exp_diff_errs, xerr = 0, fmt='ko')

pyplot.text(xmax*0.70,0.83, 'nbar = {:.2f}'.format(nb()))
pyplot.text(xmax*0.70,0.88, 'Rabi Frequency f = {:.2f} kHz'.format(f_Rabi()*10**(-3)))
pyplot.tick_params(axis='x', labelsize=size*20)
pyplot.tick_params(axis='y', labelsize=size*20)
pyplot.title('Operator Distance for Dephasing at '+dephasing_time_string+' Time',fontsize=size*30)

fig2 = pyplot.figure()

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

#m=pylab.unravel_index(np.array(flop_fit_y_axis).argmax(), np.array(flop_fit_y_axis).shape)
#print 'Flop maximum at {:.2f} us'.format(detail_flop[m]*10**6)+' -> Expected optimal t0 at {:.2f} us'.format(detail_flop[m]/2.0*10**6)
#print 'Actual t0 = {}'.format(t0)

pyplot.plot(np.array(flop_x_axis)*timescale,flop_y_axis, 'ro')

yerrflop = np.sqrt((1-flop_y_axis)*flop_y_axis/(100.0*len(flop_files)))
pyplot.errorbar(np.array(flop_x_axis)*timescale, flop_y_axis, yerr=yerrflop, xerr=0,fmt='ro')
yerrdeph = np.sqrt((1-deph_y_axis)*deph_y_axis/(100.0*len(dephase_files)))
pyplot.errorbar(np.array(deph_x_axis)*timescale, deph_y_axis, yerr=yerrdeph, xerr=0,fmt='bo')
pyplot.plot(np.array(deph_x_axis)*timescale,deph_y_axis, 'bs')
pyplot.xlabel('Excitation Duration '+label, fontsize = size*22)
pyplot.ylim((0,1))
pyplot.ylabel('Population in the D-5/2 state', fontsize = size*22)
#pyplot.legend()
pyplot.text(xmax*0.60*timescale,0.80, 'nbar = {:.2f}'.format(nb()), fontsize = size*22)
pyplot.text(xmax*0.60*timescale,0.88, 'Rabi Frequency {:.1f} kHz'.format(f_Rabi()*10**(-3)), fontsize = size*22)
pyplot.title('Local detection on the first blue sideband', fontsize = size*30)
pyplot.tick_params(axis='x', labelsize=size*20)
pyplot.tick_params(axis='y', labelsize=size*20)
#save data to text file
parameter = [nb(),enb,f_Rabi()*t0,ef_Rabi*t0,time_average,1.0/len(exp_diff[average_where])*np.sqrt(np.sum(exp_diff_errs**2)),trap_frequency['MHz'],eta]
print 'saving data to text files'
np.savetxt('data/'+folder+'/dist_x_data.txt',f_Rabi()*(deph_x_axis-t0))
np.savetxt('data/'+folder+'/dist_y_data.txt',exp_diff)
np.savetxt('data/'+folder+'/dist_y_data_errs.txt',exp_diff_errs)
np.savetxt('data/'+folder+'/dist_x_theory.txt',f_Rabi()*(nicer_resolution-t0))
np.savetxt('data/'+folder+'/dist_y_theory.txt',theo_diff)
np.savetxt('data/'+folder+'/parameter.txt',parameter)

pyplot.show()