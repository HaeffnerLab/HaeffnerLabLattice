import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import numpy as np
import timeevolution as tp
from labrad import units as U

#Times (Pi/4,Pi/2,3Pi/4,Pi,3Pi/2) in f_Rabi()*t0
times = [0,2.82248786599,5.26706463777,8.93166993592,11.2328724527,17.0517062743]
averages = [0,0.0497868898282,0.154861025572,0.0655491449449,0.0163914766524,0.144700203891]
errors = [0,0.00261032973942,0.00409218262306,0.00356111112961,0.00176529911012,0.00525966957654]

nbars =[0.185634261097,0.198142962609,0.149845833923,0.165483495241,0.232721362848]
trap_frequencies = [2.7908,2.7931,2.7906,2.7937,2.794]

size=1

nbar = np.average(nbars)
trap_frequency = U.WithUnit(np.average(trap_frequencies),'MHz')

sideband = 1.0

evo=tp.time_evolution(trap_frequency, sideband, nmax = 1000)

figure = pyplot.figure()

fake_f = 100000

timescale = evo.effective_rabi_coupling(nbar)*2.0*np.pi
label = r'$\Omega t$'

pyplot.xlabel(r'Excitation time '+label,fontsize=size*22)
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

pyplot.legend(loc=2,prop={'size':size*15})
pyplot.title('Time-Averaged Distance to Assess Quantum Discord',fontsize=size*30)
pyplot.tick_params(axis='x', labelsize=size*22)
pyplot.tick_params(axis='y', labelsize=size*22)
pyplot.xticks([np.pi/4.0,3.0*np.pi/4.0,np.pi/2.0,np.pi,5.0*np.pi/4.0,3.0*np.pi/2.0],[r'$\frac{\pi}{4}$',r'$\frac{3\pi}{4}$',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$'])
pyplot.show()