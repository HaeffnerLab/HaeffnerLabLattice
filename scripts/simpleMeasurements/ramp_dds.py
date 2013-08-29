import labrad
from labrad.units import WithUnit
import numpy as np
import time

cxn = labrad.connect()
pulser = cxn.pulser
start = 90 #MHz
stop = 120 #MHz
steps = 100
iterations = 200

for i in range(iterations):
    #go forward
    for freq in np.linspace(start,stop,steps):
        pulser.frequency('radial', WithUnit(freq, 'MHz'))
    #go back
    for freq in np.linspace(stop,start,steps):
        pulser.frequency('radial', WithUnit(freq, 'MHz'))