import labrad
from labrad.units import WithUnit
import numpy as np
import time

cxn = labrad.connect()
pulser = cxn.pulser
start = 90 #MHz
stop = 120 #MHz
steps = 100
iterations = 2000

for i in range(iterations):
    pulser.output(('global397', False))
    time.sleep(0.2)
    pulser.output(('global397', True))
#     #go forward
#     for freq in np.linspace(start,stop,steps):
#         pulser.frequency('110DP', WithUnit(freq, 'MHz'))
#     #go back
#     for freq in np.linspace(stop,start,steps):
#         pulser.frequency('110DP', WithUnit(freq, 'MHz'))