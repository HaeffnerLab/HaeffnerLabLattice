import labrad
import math
import time
import numpy as np


cxn = labrad.connect()
cxn.server = cxn.data_vault
cxn.data_vault.cd('Test Histograms', True)
cxn.data_vault.new('Histogram', [('x', 'bins')], [('y','','frequency')])

a = [1, 3, 2, 4, 5, 2, 2, 3, 4, 10, 16, 16, 17, 18, 15, 17, 15, 14, 18]
hist, bins = np.histogram(a)

cxn.data_vault.add(np.vstack((bins[0:-1], hist)).transpose())

cxn.data_vault.add_parameter('Histogram', 11)
#cxn.data_vault.add_parameter('Fit', ['[]', 'Line', '[-0.0029498298822661514, 32.067818432564962]'])
#cxn.data_vault.add_parameter('Fit', ['[1, 2]', 'Parabola', '[1, 1, 1]'])
#cxn.data_vault.add_parameter('Garbage', True)
