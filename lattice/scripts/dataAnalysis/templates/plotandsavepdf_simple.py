import labrad
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
datasets = [174535,174755,175012,175234]
names = ["2012May18_{0:04d}_{1:02d}".format(x / 100, x % 100) for x in datasets]

figure = pyplot.figure()
for i,name in enumerate(names):
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',name])
    dv.open(1)
    data = dv.get().asarray
    x = data[:,0]
    y = data[:,1]
    heatingtime = dv.get_parameter('axial_heat')
    pyplot.plot(x, y, label = "heating time {0} ms".format(heatingtime))


pyplot.legend()
pyplot.xlabel( 'Axial Heat Time (sec)')
pyplot.ylabel('Flourescence Counts / Sec')
pyplot.show()
