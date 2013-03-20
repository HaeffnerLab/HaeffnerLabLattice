import timeevolution as te
from matplotlib import pyplot
import numpy as np
from labrad import units as U

tmin = 0
tmax = 0.001
t=np.linspace(tmin,tmax,1000)
evo = te.time_evolution(U.WithUnit(2.8,'MHz'), 1)
omega = 180000
nbar = 0.626127382989
#evo.state_evolution(t, 5.0, 20000)

nminusone = evo.n-1
nminusone[0]=0
omeganminusone = evo.effective_rabi_coupling(nminusone)*omega
omeganminusone[0]=0
omegan = evo.rabi_coupling*omega
p=evo.p_thermal(nbar,nshift = False)
ones = np.ones_like(t)

flop = evo.state_evolution(t, nbar, omega/(2.0*np.pi))

gg = 0.5*np.sum(np.outer(p,ones)*(np.cos(np.outer(omegan/2.0,t))**2+np.sin(np.outer(omeganminusone/2.0,t))**2),axis=0)
eg = -0.5*1.j*np.sum(np.outer(p,ones)*np.cos(np.outer(omeganminusone/2.0,t))*(np.cos(np.outer(omegan/2.0,t))-1.j*np.sin(np.outer(omeganminusone/2.0,t))),axis=0)

ee = 1-np.abs(gg)
egreal = np.real(eg)
egim = np.imag(eg)

figure = pyplot.figure()
pyplot.plot(t*10**6,flop,label='Sideband-Flop')    
pyplot.plot(t*10**6,ee,label='Excited state pop')
pyplot.plot(t*10**6,egreal,label='Coherence |e><g| real')
pyplot.plot(t*10**6,egim,label='Coherence |e><g| imaginary')
pyplot.legend(loc=4)
pyplot.show()