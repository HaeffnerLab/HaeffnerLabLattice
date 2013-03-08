"""
Update a simple plot as rapidly as possible to measure speed.
"""
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('pyqtgraph example: PlotSpeedTest')
p.setRange(QtCore.QRectF(0, -10, 5000, 20)) 
p.setLabel('bottom', 'Time', units='sec')
curve = p.plot()


x = np.arange(10**5)
y= np.random.random(10**5)
itr = 0

app.processEvents()  ## force complete redraw for every plot
while True:
    itr+=1
    curve.setData(x[0:itr],y[0:itr])
    app.processEvents()  ## force complete redraw for every plot
    
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()