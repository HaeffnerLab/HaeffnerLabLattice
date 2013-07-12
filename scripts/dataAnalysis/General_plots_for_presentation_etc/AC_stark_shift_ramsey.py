import labrad
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

dv.cd(['','Experiments','RamseyDephaseScanDuration','2013Apr05','1545_16'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y,'o-')

pyplot.title('AC Stark Shift', fontsize = 40)
pyplot.ylim([0,1])
pyplot.xlabel(r'Interaction Time ( $\mu s$ )', fontsize = 32)
pyplot.ylabel('Excitation percentage', fontsize = 32)
pyplot.tick_params('both', labelsize = 20)
pyplot.show()
