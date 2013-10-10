import labrad
import numpy as np
import matplotlib

from matplotlib import pyplot

cxn = labrad.connect()
dv = cxn.data_vault

pyplot.figure()
pyplot.title('Sideband Far Blue Dephasing -15dBm')
info = [('2339_53', 5.0),('2340_39',10.0),('2334_16',0.0)]

for dataset,dephasing in sorted(info, key = lambda x: x[1]):
    dv.cd(['','Experiments','729Experiments','RamseyDephase','2012Dec20',dataset])
    dv.open(1)
    data = dv.get().asarray.transpose()
    pyplot.plot(data[0],data[1], label = r'Dephasing {0} $\mu s$; Dataset 2012Dec20 {1} '.format(dephasing, dataset))
    
pyplot.ylabel('Excitation Probability')
pyplot.xlabel(r'Excitation Time, $\mu s$')
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()