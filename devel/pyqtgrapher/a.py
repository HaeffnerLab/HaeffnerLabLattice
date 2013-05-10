import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
v = pg.GraphicsView()

img = np.random.random((100,150))

plt = pg.PlotItem()
plt.showAxis('top')
plt.hideAxis('bottom')
view = pg.ImageView(view=plt)
view.setImage(img)
plt.setAspectLocked(False)

v.setCentralItem(plt)

win.setCentralWidget(v)

def mouseMoved(event):
    print event
    pos = event[0]  ## using signal proxy turns original arguments into a tuple
    if plt.sceneBoundingRect().contains(pos):
        vb = plt.vb
        mousePoint = vb.mapSceneToView(pos)
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())


vLine = pg.InfiniteLine(angle=90, movable=False)
hLine = pg.InfiniteLine(angle=0, movable=False)
plt.addItem(vLine, ignoreBounds=True)
plt.addItem(hLine, ignoreBounds=True)

def mouseClicked(event):
    pos = event[0].pos()
    if plt.sceneBoundingRect().contains(pos) and event[0].double():
        vb = plt.vb
        mousePoint = vb.mapToView(pos)
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())
           
proxy = pg.SignalProxy(plt.scene().sigMouseClicked, rateLimit=60, slot=mouseClicked)
 

win.show()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()