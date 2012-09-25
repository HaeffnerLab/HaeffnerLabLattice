import labrad
import math
import time
from numpy  import *

y1 = [None] * 200

x = arange(24.9, 25.1, .005)
def generateData():
    for i in range(len(x)):
        p = [.01, 25, .1, 0] #p = [gamma, center, I, offset]
        y1[i] = p[3] + p[2]*(p[0]**2/((x[i] - p[1])**2 + p[0]**2))# Lorentzian
        
generateData()
cxn = labrad.connect()
cxn.server = cxn.data_vault
cxn.data_vault.cd('Sine Curves')
cxn.data_vault.new('Lorentzian', [('x', 'num')], [('y1','Test-Spectrum','num')])
cxn.data_vault.add_parameter('Window', ['Lorentzian'])
cxn.data_vault.add_parameter('plotLive', True)
for i in range(len(x)):
    cxn.data_vault.add([x[i], y1[i]])
    data = [i, y1[i]]
    print data
    time.sleep(.01)
cxn.data_vault.add_parameter('Fit', ['[]', 'Lorentzian', '[0.01, 25.0, 0.10000000000000001, 1.4901161193880158e-08]'])

#cxn.data_vault.add_parameter('Fit', ['[]', 'Line', '[-0.0029498298822661514, 32.067818432564962]'])
#cxn.data_vault.add_parameter('Fit', ['[1, 2]', 'Parabola', '[1, 1, 1]'])
#cxn.data_vault.add_parameter('Garbage', True)
