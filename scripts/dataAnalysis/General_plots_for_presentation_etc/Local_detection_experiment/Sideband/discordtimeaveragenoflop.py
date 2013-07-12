import matplotlib

from matplotlib import pyplot
import numpy as np
import timeevolution as tp
from labrad import units as U

data=[]
points = ['piover4','piover2','3piover4','pi','3piover2']
for folder in points:
    print 'loading file {}'.format(folder)
    data.append(np.loadtxt('data/'+folder+'/parameter.txt'))

times = []
etimes = []
averages = []
errors = []
nbars=[]
enbars=[]
trap_frequencies=[]
etas=[]

#parameter = [nbar,enbar,t0,et0,time_average,error,trap_frequency,eta]
for x in data:
    nbars.append(x[0])
    enbars.append(x[1])
    times.append(x[2])
    etimes.append(x[3])
    averages.append(x[4])
    errors.append(x[5])
    trap_frequencies.append(x[6])
    etas.append(x[7])

print nbars
print enbars

size=.85

nbar = np.average(nbars)
trap_frequency = U.WithUnit(np.average(trap_frequencies),'MHz')
eta = np.average(etas)

enbar = 1.0/len(nbars)*np.sqrt(np.sum(np.array(enbars)**2))
print 'nbar = {:.3f}+-{:.3f}'.format(nbar, enbar)

sideband = 1.0

evo=tp.time_evolution(trap_frequency, sideband, nmax = 1000)

figure = pyplot.figure(figsize=(16.5,5.5))
figure.subplots_adjust(left=0.07, right=0.95, bottom=0.225, top=0.95)
ax1 = figure.add_subplot(111)

fake_f = 100000

#timescale = evo.effective_rabi_coupling(nbar)*2.0*np.pi\
timescale=2.0*np.pi*eta
label = r'$\eta\Omega t_0$'

ax1.set_xlabel(r'Preparation Duration '+label,fontsize=size*33)
ax1.set_ylim((0,0.25))
#pyplot.ylabel('Operator Distance')
#pyplot.legend()

#plot_theory_until=np.array(times).max()/(fake_f)
plot_theory_until=eta*2.0*np.pi*25/(fake_f*timescale)

fake_times = np.linspace(0,plot_theory_until,1000)
discord = evo.discord(fake_times, nbar, fake_f)
flop = evo.state_evolution(fake_times, nbar, fake_f)

pyplot.tick_params(axis='x', labelsize=size*33)
pyplot.tick_params(axis='y', labelsize=size*33)

pyplot.grid(True, 'major')

meas = ax1.plot(np.array(times)*timescale, np.array(averages), 'ko',label='Measured Average Local Distance')
ax1.errorbar(np.array(times)*timescale, np.array(averages), np.array(errors), xerr=np.array(etimes)*timescale, fmt='k*',mew=1,capsize=4,ms=2)
ax2 = ax1.twinx()
theo = ax2.plot(fake_times*fake_f*timescale,discord,'r-',label='Discord between Qubit and Motion')
#pyplot.plot(fake_times*fake_f*timescale,flop,'b-',label='Blue Sideband Rabi Flop, nbar = {:.2f}'.format(nbar))
ax2.set_ylim((0,0.5))
ax2.set_xlim((0,2.0*np.pi))
ax2.spines['right'].set_color('red')
ax2.yaxis.label.set_color('red')
ax2.tick_params(axis='y', colors='red')
# added these three lines
lns = meas + theo
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=2,prop={'size':size*24})

#pyplot.title('Time-Averaged Distance to Assess Quantum Discord',fontsize=size*30)
#pyplot.yticks((0,0.1,0.2,0.3,0.4),(0,0.1,0.2,0.3,0.4))
pyplot.xticks((0,np.pi/2,np.pi,3.0*np.pi/2,2.0*np.pi),(0,r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{3\pi}{2}$',r'$2\pi$'))
pyplot.tick_params(axis='x', labelsize=size*33)
pyplot.tick_params(axis='y', labelsize=size*33)
#pyplot.xticks([np.pi/4.0,3.0*np.pi/4.0,np.pi/2.0,np.pi,5.0*np.pi/4.0,3.0*np.pi/2.0],[r'$\frac{\pi}{4}$',r'$\frac{3\pi}{4}$',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$'])

print 'parameters:\n nbar = {} \n trap frequency = {}\n eta = {}'.format(nbar,trap_frequency,eta)
print 'measured times are {}'.format(np.array(times)*timescale)

pyplot.show()