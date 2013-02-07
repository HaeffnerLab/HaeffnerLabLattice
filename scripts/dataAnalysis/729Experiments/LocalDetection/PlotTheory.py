import TheoryPrediction as tp

nb=5.
maxn=2000.
pl=tp.plots(nb,sideband=1.,state='therm')# Be-9 omega=2*np.pi*500000.,nu=2*np.pi*11200000.
pl.makeplot(tmin=0.,tmax=10.,steps=250.,t0=1.49,amax=maxn,nmax=500.,num=False,statusreport=False,dephasing=True,lsig=False,discord=False,coh=True)
#pl.frequencies(maxn,nmax=200,detail=True)
tp.pyplot.show()
#pl.numcontour(0.,5.,0.,5.,50.,nmax=50.,statusreport=True)
#pl.contour(0.,10000.,t0min=0,t0max=100.,steps=500.,amax=40.,showopt=False)
