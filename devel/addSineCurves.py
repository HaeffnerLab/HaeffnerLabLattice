import labrad
import math
import time
from numpy  import *

y1 = [None] * 100000
y2 = [None] * 100000
y3 = [None] * 100000


def generateData():
    for i in range(99999):
        y1[i] = math.sin(i)+ 2
        y2[i] = math.cos(i)+ 32
        y3[i] = math.sin(i)+ 64
generateData()
cxn = labrad.connect()
cxn.server = cxn.data_vault
cxn.data_vault.cd('Sine Curves')
cxn.data_vault.new('Sine Curves', [('x', 'num')], [('y1','866 ON','num'),('y2','866 OFF','num'),('y3','Differential Signal','num')])
cxn.data_vault.add_parameter('Window', ['sine curve!'])
cxn.data_vault.add_parameter('plotLive', True)
for i in range(100000):
    cxn.data_vault.add([i, y1[i], y2[i], y3[i]])
    data = [i, y1[i], y2[i], y3[i]]
    print data
    time.sleep(.25)
#cxn.data_vault.add_parameter('Fit', ['[]', 'Line', '[-0.0029498298822661514, 32.067818432564962]'])
#cxn.data_vault.add_parameter('Fit', ['[1, 2]', 'Parabola', '[1, 1, 1]'])
#cxn.data_vault.add_parameter('Garbage', True)
