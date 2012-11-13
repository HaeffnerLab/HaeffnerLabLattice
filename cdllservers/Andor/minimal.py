import sys
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib import cm
import time

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from datetime import datetime




from matplotlib.widgets import RectangleSelector 
import numpy as np

a = QtGui.QApplication( [] )
import qt4reactor
qt4reactor.install()

from labrad.server import LabradServer, setting

EMGAIN = 255
EXPOSURE = .3 #sec

class Canvas(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, parent):
        self.parent = parent
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.cnt = 0
        
        
    def newAxes(self, hstart, hend, vstart, vend):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        print hstart, hend, vstart, vend
        self.im = self.ax.imshow(self.data, extent=[hstart, hend, vstart, vend], origin='lower', interpolation='nearest')#, cmap=cm.hot)#gist_heat)
        self.setupSelector()


    def updateData(self, data, width, height):
        try:
            self.data = np.reshape(data, (height, width))
        except ValueError:
            pass # happens if update data is called before the new width and height are calculated upon changing the image size

        self.im.set_data(self.data)
        self.im.axes.figure.canvas.draw()
   
    def onselect(self, eclick, erelease):
        'eclick and erelease are matplotlib events at press and release'
        print ' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata)
        print ' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata)
          
        if (eclick.ydata > erelease.ydata):
            eclick.ydata, erelease.ydata= erelease.ydata, eclick.ydata
        if (eclick.xdata > erelease.xdata):
            eclick.xdata, erelease.xdata = erelease.xdata, eclick.xdata
        
        # data sent will always have the eclick point be the left point and the erelease point be the right point
        self.parent.parent.changeImageRegion(int(eclick.xdata), int(eclick.ydata), int(erelease.xdata), int(erelease.ydata))
    
    def setupSelector(self):
        self.rectSelect = RectangleSelector(self.ax, self.onselect, drawtype='box', rectprops = dict(facecolor='red', edgecolor = 'white',
                 alpha=0.5, fill=False))   
        
class AppWindow(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
        self.cmon = Canvas(self)
        self.cmon.show()
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.cmon, self)
        
        layout = QtGui.QVBoxLayout()

        # Layout that involves the canvas, toolbar, graph options...etc.
        layout.addWidget(ntb)
        layout.addWidget(self.cmon)
        
        
        temperatureButton = QtGui.QPushButton("Temp", self)
        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        temperatureButton.clicked.connect(self.printTemperature)     
        
        liveVideoButton = QtGui.QPushButton("Live", self)
        liveVideoButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        liveVideoButton.clicked.connect(self.liveVideo)
        
        abortButton = QtGui.QPushButton("Abort Video", self)
        abortButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        abortButton.clicked.connect(self.abortVideo)
        
        resetScaleButton = QtGui.QPushButton("Reset Scale", self)
        resetScaleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        resetScaleButton.clicked.connect(self.resetScale)
        
        emGainLabel = QtGui.QLabel()
        emGainLabel.setText('EM Gain: ')
        
        self.emGainSpinBox = QtGui.QSpinBox()
        self.emGainSpinBox.setMinimum(0)
        self.emGainSpinBox.setMaximum(255)
        self.emGainSpinBox.setSingleStep(1)  
        self.emGainSpinBox.setValue(EMGAIN)     
        self.emGainSpinBox.setKeyboardTracking(False)
        self.connect(self.emGainSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeEMGain)

        exposureLabel = QtGui.QLabel()
        exposureLabel.setText('Exposure (ms): ')
        
        self.exposureSpinBox = QtGui.QSpinBox()
        self.exposureSpinBox.setMinimum(100)
        self.exposureSpinBox.setMaximum(1000)
        self.exposureSpinBox.setSingleStep(1)  
        self.exposureSpinBox.setValue(EXPOSURE*1000)     
        self.exposureSpinBox.setKeyboardTracking(False)
        self.connect(self.exposureSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeExposure)

        
         # Layout
        self.bottomPanel1 = QtGui.QHBoxLayout()
        
        self.bottomPanel1.addWidget(temperatureButton)
        self.bottomPanel1.addWidget(liveVideoButton)
        self.bottomPanel1.addWidget(abortButton)
        self.bottomPanel1.addWidget(resetScaleButton)
        self.bottomPanel1.addWidget(emGainLabel)
        self.bottomPanel1.addWidget(self.emGainSpinBox)
        self.bottomPanel1.addWidget(exposureLabel)
        self.bottomPanel1.addWidget(self.exposureSpinBox)
    
        self.bottomPanel1.addStretch(0)
        self.bottomPanel1.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        layout.addLayout(self.bottomPanel1)
               
        self.setLayout(layout)

    def changeEMGain(self, value):
        self.parent.parent.ChangeEMCCDGain(self.emGainSpinBox.value())

    def changeExposure(self, value):
        if (self.parent.live == True):
            self.parent.abortVideo()
            self.parent.parent.ChangeExposure(float(self.exposureSpinBox.value())/1000) #convert ms to s
            self.parent.liveVideo()
        else:
            self.parent.parent.ChangeExposure(float(self.exposureSpinBox.value())/1000) #convert ms to s               

    def abortVideo(self, evt):
        self.parent.live = False
        yield self.parent.parent.AbortAcquisition()

    def printTemperature(self, evt):
        tempError = self.parent.parent.GetCurrentTemperature()
        temp = self.parent.parent.currentTemperature
        print temp, tempError
   
    def liveVideo(self, evt):
        self.parent.liveVideo()
        
    def resetScale(self, evt):
        self.parent.hstart = self.parent.originalHStart
        self.parent.hend = self.parent.originalHEnd
        self.parent.vstart = self.parent.originalVStart
        self.parent.vend = self.parent.originalVEnd
        self.parent.width = self.parent.hend - self.parent.hstart
        self.parent.height = self.parent.vend - self.parent.vstart
        if (self.parent.live == True):
            self.abortVideo(1)
            error = self.parent.parent.SetImage(1,1,self.parent.hstart,self.parent.hend,self.parent.vstart,self.parent.vend)
            print 'image: ', error
            self.parent.liveVideo()
        else:
            error = self.parent.parent.SetImage(1,1,self.parent.hstart,self.parent.hend,self.parent.vstart,self.parent.vend)
            print 'image error: ', error

        
    def closeEvent(self, evt):
        self.parent.parent.abortVideo()
        try:
            self.killTimer(self.cmon.timer)
        except AttributeError:
            pass 
        self.parent.reactor.stop() 
        
class MinimalServer(LabradServer):
    """This docstring will appear in the LabRAD helptext."""
    name = "Minimal Server"
    
    def initServer(self):
        self.win = AppWindow(self)
        self.win.show()        
        

    @setting(10, "Echo", data="?", returns="?")
    def echo(self, c, data):
        """This docstring will appear in the setting helptext."""
        print type(data)
        return data

if __name__ == "__main__":
    from labrad import util
    util.runServer(MinimalServer())