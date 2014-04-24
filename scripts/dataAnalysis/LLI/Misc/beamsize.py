import labrad
import numpy as np
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()
distance = np.array([0.0, 50.0, 150.0, 250.0, 350.0, 450.0, 550.0,650.0,750.0, 850.0])
ion0 = np.array([36309.0, 39880.0, 38309.0, 29759.0, 19074.0, 10151.0, 6630.0, 4778.0, 1958.0,0.0])
ion1 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0,5631.0,13000.0, 23834.0])


#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
#pyplot.ylabel('Parity signal')
#pyplot.xlabel('Time (us)')
#ion-ion distance is 11 um
# 86 positions / micron
# beam size is 5.5 microns (FWHM)

pyplot.plot(distance, ion0, 'o-')
pyplot.plot(distance, ion1, 'o-')
pyplot.plot(distance+950, ion0, 'o-')
pyplot.show()
