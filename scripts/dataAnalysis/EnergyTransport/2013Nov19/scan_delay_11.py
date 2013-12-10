import labrad
from matplotlib import pyplot
import numpy as np
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault


date = '2013Nov18'
left = '1434_34'; OP_reduction_left = 1#0.43
center = '1452_28'; OP_reduction_center =1# 0.75
right = '1459_55'; OP_reduction_right = 1#0.95
#left, 11
pyplot.subplot(311)
dv.cd(['','Experiments','Blue Heat ScanDelay',date,left])
dv.open(1)
data = dv.get().asarray
delays,excitations = data.transpose()
excitations = excitations / OP_reduction_left
pyplot.plot(delays,excitations,'*-')
# pyplot.xlabel(r'Delay after heat $\mu s$')
pyplot.ylabel('Scaled Excitation')
pyplot.title('11 ions, left ion')
pyplot.grid(True, 'both')
pyplot.ylim(0,1)
#center, 11
pyplot.subplot(312)
dv.cd(['','Experiments','Blue Heat ScanDelay',date,center])
dv.open(1)
data = dv.get().asarray
delays,excitations = data.transpose()
excitations = excitations / OP_reduction_center
pyplot.plot(delays,excitations,'*-')
pyplot.xlabel(r'Delay after heat $\mu s$')
pyplot.ylabel('Scaled Excitation ')
pyplot.title('11 ions, center ion')
pyplot.grid(True, 'both')
pyplot.ylim(0,1)
#right, 11
pyplot.subplot(313)
dv.cd(['','Experiments','Blue Heat ScanDelay',date,center])
dv.open(1)
data = dv.get().asarray
delays,excitations = data.transpose()
excitations = excitations / OP_reduction_right
pyplot.plot(delays,excitations,'*-')
pyplot.xlabel(r'Delay after heat $\mu s$')
pyplot.ylabel('Scaled Excitation')
pyplot.title('11 ions, right ion')
pyplot.grid(True, 'both')
pyplot.ylim(0,1)





pyplot.tight_layout()
pyplot.show()
