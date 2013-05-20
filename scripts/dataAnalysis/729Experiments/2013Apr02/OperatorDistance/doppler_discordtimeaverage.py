import matplotlib

from matplotlib import pyplot
import numpy as np
import timeevolution as tp
from labrad import units as U


#Times (Pi/4,Pi/2,3Pi/4,Pi,3Pi/2) in f_Rabi()*t0
times = [0,2.82713003685,5.27355837955,8.8792654291,11.2252501165,17.2867104081]
averages = [0,0.0497868898282,0.154861025572,0.0655491449449,0.0163914766524,0.144347495801]
errors = [0,0.00261032973942,0.00409218262306,0.00341273149921,0.00176529911012,0.00525374485925]

nbars =[0.185631982212,0.198141427699,0.123993486485,0.167394549013,0.217396568974]
trap_frequencies = []

nbar = np.average(nbars)
trap_frequency = np.average(trap_frequencies)
sideband = 1.0

evo=tp.time_evolution(trap_frequency, sideband, nmax = 1000)

figure = pyplot.figure()

fake_f = 100000

timescale = evo.effective_rabi_coupling(nbar)*2.0*np.pi
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