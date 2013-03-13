import TheoryPrediction as tp
import numpy as np

nb=30.
maxn=2000.
pl=tp.plots(nb,sideband=0,state='therm',nu=2.*np.pi*2800000)# Be-9 omega=2*np.pi*500000.,nu=2*np.pi*11200000.
pl.makeplot(tmin=0.,tmax=10.,steps=1000.,t0=1.49,amax=maxn,nmax=500.,num=False,statusreport=False,dephasing=False,lsig=False,discord=False,coh=True)
#pl.frequencies(maxn,nmax=200,detail=True)
tp.pyplot.show()
#pl.numcontour(0.,5.,0.,5.,50.,nmax=50.,statusreport=True)
#pl.contour(0.,10000.,t0min=0,t0max=100.,steps=500.,amax=40.,showopt=False)