import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore

pg.mkQApp()  # builds QApplication

## create and show PlotWidget as a container for other items
pw = pg.PlotWidget()
pw.show()

## create image and set its position/size
imgData = np.random.normal(size=(100,100))
img = pg.ImageItem(imgData)
img.setRect(QtCore.QRectF(0, 0, 2, 2))
img.setLevels([-2, 10]) ## Make image appear darker so curve stands out
pw.addItem(img)

## create a red curve initially with no points
curve = pg.PlotCurveItem(pen='r')
pw.addItem(curve)

## every 50ms, run update() to change the data displayed in the curve
angle = 0
def update():
    global angle
    angle += .05
    x = np.sin(np.linspace(0, 2*np.pi, 7)+angle)+1
    y = np.cos(np.linspace(0, 2*np.pi, 7)+angle)+1
    curve.setData(x, y)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()