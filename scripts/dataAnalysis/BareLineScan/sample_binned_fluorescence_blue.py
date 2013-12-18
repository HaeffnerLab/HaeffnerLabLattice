from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg
from scipy import special as bessel
import labrad
import lmfit

cxn = labrad.connect('192.168.169.197')
dv = cxn.data_vault
dv.cd('','Experiments','BareLineScan','2013Nov16','1601_56')
dv.open(11)
data_blue=dv.get().asarray
data_blue[:,0] = (data_blue[:,0]*1000000-3)%12
data_blue_x = data_blue[:,0]
data_blue_y = data_blue[:,1]


dv.cd('','Experiments','BareLineScanRed','2013Nov18','1923_14')
dv.open(32)
data_red=dv.get().asarray
data_red[:,0]=(data_red[:,0]*1000000-3)%18.8
data_red_x = data_red[:,0]
data_red_y = data_red[:,1]

#pyplot.plot(data_blue[:,0],data_blue[:,1],'o')
#pyplot.plot(data_red_x[0:30],data_red_y[0:30],'-b')
#pyplot.plot(data_red_x[31:data_red_x.size],data_red_y[31:data_red_x.size],'-b')
#pyplot.plot(np.hstack((data_blue_x[31:data_blue_x.size],data_blue_x[0:30])),np.hstack((data_blue_y[31:data_blue_x.size],data_blue_y[0:30]))+1000000000,'-b',linewidth=1.5)
pyplot.plot(np.hstack((data_red_x[31:data_red_x.size],data_red_x[0:30])),np.hstack((data_red_y[31:data_red_x.size],data_red_y[0:30]))+1000000000,'-b',linewidth=1.5)
#pyplot.plot(data_blue_x[31:data_blue_x.size],data_blue_y[31:data_blue_x.size], '-b',linewidth=1.5)
pyplot.show()