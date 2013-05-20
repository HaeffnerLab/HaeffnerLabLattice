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
ax1 = figure.add_subplot(111)

fake_f = 100000

#timescale = evo.effective_rabi_coupling(nbar)*2.0*np.pi\
timescale=2.0*np.pi
label = r'$\Omega t_0$'

ax1.set_xlabel(r'Dephasing Time '+label,fontsize=size*33)
ax1.set_ylim((0,0.25))
#pyplot.ylabel('Operator Distance')
#pyplot.legend()

#plot_theory_until=np.array(times).max()/(fake_f)
plot_theory_until=2.0*np.pi*25/(fake_f*timescale)

fake_times = np.linspace(np.array(times).min()/(fake_f),plot_theory_until,1000)
discord = evo.discord(fake_times, nbar, fake_f)
flop = evo.state_evolution(fake_times, nbar, fake_f)

pyplot.tick_params(axis='x', labelsize=size*33)
pyplot.tick_params(axis='y', labelsize=size*33)

pyplot.grid(True, 'major')

meas = ax1.plot(np.array(times)*timescale, np.array(averages), 'ko',label='Measured Average Local Distance')
ax1.errorbar(np.array(times)*timescale, np.array(averages), np.array(errors), xerr=0, fmt='k*',mew=1,capsize=4,ms=2)
ax2 = ax1.twinx()
theo = ax2.plot(fake_times*fake_f*timescale,discord,'r-',label='Discord between Qubit and Motion')
#pyplot.plot(fake_times*fake_f*timescale,flop,'b-',label='Blue Sideband Rabi Flop, nbar = {:.2f}'.format(nbar))
ax2.set_ylim((0,0.5))
ax2.set_xlim((0,155))
ax2.spines['right'].set_color('red')
ax2.yaxis.label.set_color('red')
ax2.tick_params(axis='y', colors='red')
# added these three lines
lns = meas + theo
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=2,prop={'size':size*25})

#pyplot.title('Time-Averaged Distance to Assess Quantum Discord',fontsize=size*30)
pyplot.tick_params(axis='x', labelsize=size*33)
pyplot.tick_params(axis='y', labelsize=size*33)
#pyplot.xticks([np.pi/4.0,3.0*np.pi/4.0,np.pi/2.0,np.pi,5.0*np.pi/4.0,3.0*np.pi/2.0],[r'$\frac{\pi}{4}$',r'$\frac{3\pi}{4}$',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$'])

print 'parameters:\n nbar = {} \n trap frequency = {}'.format(nbar,trap_frequency)
print 'measured times are {}'.format(np.array(times)*timescale)

pyplot.show()