import labrad
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

figure = pyplot.figure()
figure.clf()


dv.cd(['','Experiments','Blue Heat ScanDelay','2013Oct21','1837_52'])
dv.open(1)
data = dv.get().asarray
t = data[:,0]
ion0 = data[:,1]
ion5 = data[:,5]




pyplot.plot(t, ion0,'bo-', label = 'ion 0')
pyplot.plot(t, ion5,'ro-', label = 'ion 5')

dv.cd(['','Experiments','Blue Heat ScanDelay','2013Oct21','1855_28'])
dv.open(1)
data = dv.get().asarray
t = data[:,0]
ion0 = data[:,1]
ion5 = data[:,5]
pyplot.plot(t, ion0,'bo-')
pyplot.plot(t, ion5,'ro-')

# dv.cd(['','Experiments','Blue Heat ScanDelay','2013Oct21','1914_02'])
# dv.open(1)
# data = dv.get().asarray
# t = data[:,0]
# ion0 = data[:,1]
# ion5 = data[:,5]
# pyplot.plot(t, ion0,'bo-')
# pyplot.plot(t, ion5,'ro-')

# pyplot.tight_layout()
pyplot.title('Energy Transport, 5 ions', fontsize = 32)
pyplot.ylim([0,1])
pyplot.xlabel(r'Delay after heat $\mu s$', fontsize = 26)
pyplot.ylabel('Excitation', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend()

pyplot.show()
