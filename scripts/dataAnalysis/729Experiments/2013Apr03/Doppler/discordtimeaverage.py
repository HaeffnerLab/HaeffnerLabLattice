import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import numpy as np
import timeevolution as tp
from labrad import units as U


#Times (Pi/4,Pi/2,3Pi/4,Pi,3Pi/2) in f_Rabi()*t0
times = [0,1.01111818751,2.03297689874,2.42986170722,4.16730766416,4.80000901809,6.04239013812]#,23.6608727504]
averages = [0,0.00949216930617,0.0277187091903,0.0226461508916,0.0146028881627,0.0139644038232,0.0169004157706]#,0.00206158698092]
errors = [0,0.00105121600544,0.0016338246519,0.00158316755754,0.00131982414498,0.00135874891692,0.00149356106556]#,0.000872225718094]

nbars =[8.24409435163,5.88040102288,11.0772139565,8.07677326831,8.28682525321,6.1128257215]#,4.37743173499]
trap_frequencies = [2.8318,2.8474,2.8282,2.8306,2.83,2.8288]#,2.8317]

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
pyplot.ylim((0,0.7))
#pyplot.ylabel('Operator Distance')
#pyplot.legend()

fake_times = np.linspace(np.array(times).min()/(fake_f),np.array(times).max()/(fake_f),1000)
discord = evo.discord(fake_times, nbar, fake_f)
flop = evo.state_evolution(fake_times, nbar, fake_f)

pyplot.plot(np.array(times)*timescale,10*2.0*np.array(averages),'ko',label='Time-Averaged Qubit Distance')
pyplot.plot(fake_times*fake_f*timescale,10*discord,'k-',label='Discord between Qubit and Motion')
pyplot.plot(fake_times*fake_f*timescale,flop,'b-',label='Blue Sideband Rabi Flop, nbar = {:.2f}'.format(nbar))
pyplot.errorbar(np.array(times)*timescale, 10*2.0*np.array(averages), 10*2.0*np.array(errors), xerr=0, fmt='ko')

pyplot.legend(loc=2,prop={'size':size*15})
pyplot.title('Time-Averaged Distance to Assess Quantum Discord',fontsize=size*30)
pyplot.tick_params(axis='x', labelsize=size*22)
pyplot.tick_params(axis='y', labelsize=size*22)
pyplot.xticks([np.pi/4.0,3.0*np.pi/4.0,np.pi/2.0,np.pi,5.0*np.pi/4.0,3.0*np.pi/2.0],[r'$\frac{\pi}{4}$',r'$\frac{3\pi}{4}$',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$'])
pyplot.show()