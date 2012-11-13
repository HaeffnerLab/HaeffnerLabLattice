import labrad
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure()
dv.cd(['','Experiments','729Experiments','Spectrum','2012Aug29','1447_20'])
dv.open(1)
data = dv.get().asarray
x_axis = ((data[:,0]-204.598)*1000-0.354)*2
y_axis = data[:,1]
print y_axis
### two current sources ###
#thorlabs = data[0,7660]
#ilx = data[76701:116194]

##normalize

#thorlabs_i = thorlabs[:,1]-np.average(thorlabs[:,1])
#ilx_i = ilx[:,1]-np.average(ilx[:,1])

pyplot.plot(x_axis,y_axis, 'o')

pyplot.xlabel( 'Frequency (kHz)')
pyplot.ylabel('Excitation probability')
pyplot.title('Excitation spectrum of 729 nm transition')
pyplot.ylim([0,0.7])
pyplot.xlim([-10,10])
pyplot.show()
