import labrad
from matplotlib import pyplot
# import numpy as np
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#5 ions
# date = '2013Nov20'
# left = '1558_38'; OP_reduction_left = 0.547
# center = '1618_53'; OP_reduction_center = 0.620
# right = '1649_34'; OP_reduction_right = 0.854
#15 ions
# date = '2013Nov20'
# left = '1743_03'; OP_reduction_left = 0.5
# center = '1819_08'; OP_reduction_center = 0.596
# right = '1920_13'; OP_reduction_right = 0.869
#25 ions
date = '2013Nov20'
left = '2035_00'; OP_reduction_left = 0.466
center = '2116_22'; OP_reduction_center = 0.866
right = '2139_53'; OP_reduction_right = 1.021

#left, 5
pyplot.subplot(111)
dv.cd(['','Experiments','Blue Heat ScanDelay',date,left])
dv.open(1)
data = dv.get().asarray
delays,excitations = data.transpose()
excitations = excitations / OP_reduction_left
pyplot.plot(delays,excitations,'-')
dv.cd(['','Experiments','Blue Heat ScanDelay',date,center])
dv.open(1)
data = dv.get().asarray
delays,excitations = data.transpose()
excitations = 2 + excitations / OP_reduction_center
pyplot.plot(delays,excitations,'-k')
dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
dv.open(1)
data = dv.get().asarray
delays,excitations = data.transpose()
excitations = 1 + excitations / OP_reduction_right
pyplot.plot(delays,excitations,'-r')
pyplot.ylim(0,3)
pyplot.show()