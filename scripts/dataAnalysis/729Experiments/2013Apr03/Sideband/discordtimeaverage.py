import matplotlib

from matplotlib import pyplot
import numpy as np
import timeevolution as tp
from labrad import units as U

data=[]
points = ['piover4','piover2','3piover4','pi','3piover2']
for folder in points:
    print 'loading file {}'.format(folder)
    data.append(np.loadtxt('data/average/'+folder+'.txt'))

times = [0]
averages = [0]
errors = [0]
nbars=[]
trap_frequencies=[]

for x in data:
    times.append(x[0])
    averages.append(x[1])
    errors.append(x[2])
    nbars.append(x[3])
    trap_frequencies.append(x[4])

print nbars

size=1

nbar = np.average(nbars)
trap_frequency = U.WithUnit(np.average(trap_frequencies),'MHz')

sideband = 1.0

evo=tp.time_evolution(trap_frequency, sideband, nmax = 1000)

figure = pyplot.figure()

fake_f = 100000

#timescale = evo.effective_rabi_coupling(nbar)*2.0*np.pi\
timescale=2.0*np.pi
label = r'$\Omega t$'

pyplot.xlabel(r'Excitation time '+label,fontsize=size*22)
pyplot.ylim((0,1))
#pyplot.ylabel('Operator Distance')
#pyplot.legend()

#plot_theory_until=np.array(times).max()/(fake_f)
plot_theory_until=2.0*np.pi*25/(fake_f*timescale)

fake_times = np.linspace(np.array(times).min()/(fake_f),plot_theory_until,1000)
discord = evo.discord(fake_times, nbar, fake_f)
flop = evo.state_evolution(fake_times, nbar, fake_f)

pyplot.plot(np.array(times)*timescale,2.0*np.array(averages),'ko',label='Time-Averaged Qubit Distance')
pyplot.plot(fake_times*fake_f*timescale,discord,'k-',label='Discord between Qubit and Motion')
pyplot.plot(fake_times*fake_f*timescale,flop,'b-',label='Blue Sideband Rabi Flop, nbar = {:.2f}'.format(nbar))
pyplot.errorbar(np.array(times)*timescale, 2.0*np.array(averages), 2.0*np.array(errors), xerr=0, fmt='ko',ms=.1)

pyplot.legend(loc=2,prop={'size':size*15})
pyplot.title('Time-Averaged Distance to Assess Quantum Discord',fontsize=size*30)
pyplot.tick_params(axis='x', labelsize=size*22)
pyplot.tick_params(axis='y', labelsize=size*22)
#pyplot.xticks([np.pi/4.0,3.0*np.pi/4.0,np.pi/2.0,np.pi,5.0*np.pi/4.0,3.0*np.pi/2.0],[r'$\frac{\pi}{4}$',r'$\frac{3\pi}{4}$',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$'])

print 'parameters:\n nbar = {} \n trap frequency = {}'.format(nbar,trap_frequency)
print 'measured times are {}'.format(np.array(times)*timescale)

pyplot.show()