"""
Update a simple plot as rapidly as possible to measure speed.
"""
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
app = QtGui.QApplication([])


my_widget = QtGui.QWidget()
my_layout = QtGui.QHBoxLayout()
spin = QtGui.QSpinBox()




pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

my_layout.addWidget(spin)
spin.setLayout(my_layout)

my_widget.show()
p = pg.plot()




p.setWindowTitle('pyqtgraph example: PlotSpeedTest')
p.setRange(QtCore.QRectF(0, -10, 5000, 20)) 
p.setLabel('bottom', 'Time', units='sec')
p.setTitle('Fake PMT Counts')
p.showButtons()
p.addLegend()
#p.showGrid(True, True, 0.1)

curve = p.plot(name = 'my black curve')

pen = pg.mkPen(color = 'k')
curve.setPen(pen)

another_curve = p.plot(name = 'my red curve')
another_curve.setPen(pg.mkPen(color = 'r'))

print p.listDataItems()


x = np.arange(10**5)
y= np.random.random(10**5)
itr = 0
import time
t = time.time()
app.processEvents()  ## force complete redraw for every plot
while True:
    itr+=1
    curve.clear()
    another_curve.clear()
    curve.setData(x[0:itr],y[0:itr])
    another_curve.setData(x[0:itr],5 + y[0:itr])
    app.processEvents()  ## force complete redraw for every plot
    
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()