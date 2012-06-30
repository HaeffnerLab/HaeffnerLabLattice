import labrad
import numpy as np

cxn = labrad.connect()
min = cxn.minimal_server

arr = [[1, 2, 3], [4, 5, -1]]
#arr2 = np.reshape(arr, (2, 3))
#print arr2

print min.echo(arr)

#from matplotlib.pylab import *
#import numpy as np
#
#rawdata = np.loadtxt(r'C:\Users\lattice\Documents\Andor\jun12\062812\8\image72')
#matshow(rawdata)
#show()

#import time
#import labrad
#cxn = labrad.connect()
#server = cxn.andor_server
#temp = server.get_current_temperature()
#print temp
#
#server.set_trigger_mode(1)
#server.set_read_mode(4)
#server.set_emccd_gain(255)
#server.set_exposure_time(.1)   
#server.cooler_on()
#
#server.set_acquisition_mode(3)
#server.set_number_kinetics(90)
#            
#server.start_acquisition_kinetic_external()
#for i in range(90):
#    time.sleep(.2)
#    status = server.get_series_progress()
#    print status
#print 'done'
