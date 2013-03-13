import TheoryPrediction as tp
from matplotlib import pyplot
import numpy as np
import random

nb=5.
maxn=2000.

#pl=tp.plots(nb,sideband=0,state='therm',nu=2.*np.pi*2800000)# Be-9 omega=2*np.pi*500000.,nu=2*np.pi*11200000.
#pl.rabiflop(tmin=0.,tmax=10.,steps=1000.,t0=1.49,amax=maxn,nmax=500.,num=False,statusreport=False,dephasing=False,lsig=False,discord=False,coh=True)
#pl.frequencies(maxn,nmax=200,detail=True)
#tp.pyplot.show()
#pl.numcontour(0.,5.,0.,5.,50.,nmax=50.,statusreport=True)
#pl.contour(0.,10000.,t0min=0,t0max=100.,steps=500.,amax=40.,showopt=False)

detuning=0
fluctuations=0.02
omega_center=40000.
n=100

flops=[]
for i in range(n):
    x=random.uniform(-1,1)*fluctuations
    sb=tp.Sideband(nb, sideband=0,omega=2.*np.pi*omega_center*(1.+x),nu=2.*np.pi*2800000)
    sb.anaplot(0, 200*10**-6*sb.p.omega/(2.*np.pi), 500, 0, dephasing=False, discord=False, lsig=False)
    flops.append(sb.flop)

flops=np.sum(flops,axis=0)/np.float32(n)
sb.x=2.*np.pi*sb.x/sb.p.omega

sb_nondeph=tp.Sideband(nb, sideband=0,omega=2.*np.pi*omega_center,nu=2.*np.pi*2800000)
sb_nondeph.anaplot(0, 200*10**-6/(2.*np.pi)*sb_nondeph.p.omega, 500, 0, dephasing=False, discord=False, lsig=False)
sb_nondeph.x=2.*np.pi*sb_nondeph.x/sb_nondeph.p.omega

figure = pyplot.figure()    
pyplot.plot(sb.x*10**6,flops)
pyplot.plot(sb_nondeph.x*10**6,sb_nondeph.flop)
pyplot.show()