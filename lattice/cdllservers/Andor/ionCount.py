import sys
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib import cm
import time

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from datetime import datetime




from matplotlib.widgets import RectangleSelector 
import numpy as np

EMGAIN = 255
EXPOSURE = .3 #sec
       
        
class AppWindow(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
       
        layout = QtGui.QVBoxLayout()
       
        
        temperatureButton = QtGui.QPushButton("Temp", self)
        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        temperatureButton.clicked.connect(self.printTemperature)     
        
        ionCountButton = QtGui.QPushButton("Count Ions", self)
        ionCountButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        ionCountButton.clicked.connect(self.ionCount) 
        
        exposureLabel = QtGui.QLabel()
        exposureLabel.setText('Exposure (ms): ')

        iterationsLabel = QtGui.QLabel()
        iterationsLabel.setText('Iterations: ')
        
        thresholdLabel = QtGui.QLabel()
        thresholdLabel.setText('Threshold: ')
        
        self.exposureSpinBox = QtGui.QSpinBox()
        self.exposureSpinBox.setMinimum(100)
        self.exposureSpinBox.setMaximum(1000)
        self.exposureSpinBox.setSingleStep(1)  
        self.exposureSpinBox.setValue(EXPOSURE*1000)     
        self.exposureSpinBox.setKeyboardTracking(False)
        self.connect(self.exposureSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeExposure)

        self.iterationsSpinBox = QtGui.QSpinBox()
        self.iterationsSpinBox.setMinimum(0)
        self.iterationsSpinBox.setMaximum(1000)
        self.iterationsSpinBox.setSingleStep(1)  
        self.iterationsSpinBox.setValue(2)     
        self.iterationsSpinBox.setKeyboardTracking(False)

        self.thresholdSpinBox = QtGui.QSpinBox()
        self.thresholdSpinBox.setMinimum(0)
        self.thresholdSpinBox.setMaximum(1000)
        self.thresholdSpinBox.setSingleStep(1)  
        self.thresholdSpinBox.setValue(500)     
        self.thresholdSpinBox.setKeyboardTracking(False)

         # Layout
        self.bottomPanel1 = QtGui.QHBoxLayout()
        
        self.bottomPanel1.addWidget(temperatureButton)
        self.bottomPanel1.addWidget(ionCountButton)
    
        self.bottomPanel1.addStretch(0)
        self.bottomPanel1.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        self.bottomPanel1.addWidget(iterationsLabel)
        self.bottomPanel1.addWidget(self.iterationsSpinBox)
        self.bottomPanel1.addWidget(thresholdLabel)
        self.bottomPanel1.addWidget(self.thresholdSpinBox)
        self.bottomPanel1.addWidget(exposureLabel)
        self.bottomPanel1.addWidget(self.exposureSpinBox)

        layout.addLayout(self.bottomPanel1)
             
        self.setLayout(layout)

    def printTemperature(self, evt):
        self.parent.printTemperature()
    
    def ionCount(self, evt):
        self.parent.ionCount(self.thresholdSpinBox.value(), self.iterationsSpinBox.value())
    
    def changeExposure(self, value):
        self.parent.changeExposure(float(self.exposureSpinBox.value())/1000) #convert ms to s       

    def closeEvent(self, evt):
        self.parent.reactor.stop()           

class IonCount():
    def __init__(self, reactor):
        self.reactor = reactor
        self.live = False
        self.connect()

    def openVideoWindow(self):
        self.win = AppWindow(self)
        self.win.show()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        try:
            self.server = yield self.cxn.andor_ion_count
            self.setupCamera()
        except Exception ,e:
            print 'server not connected: {}'.format(e)
   
    @inlineCallbacks
    def setupCamera(self):
        temp = yield self.server.get_current_temperature()
        print temp
        
        try:
            yield self.server.set_trigger_mode(0)
        except:
            print 'client not closed properly'
            self.abortVideo()
            yield self.server.set_trigger_mode(0)
        yield self.server.set_read_mode(4)
        yield self.server.set_emccd_gain(EMGAIN)
        yield self.server.set_exposure_time(EXPOSURE)   
        yield self.server.cooler_on()
        
        
        #self.detectorDimensions = yield self.server.get_detector_dimensions() #this gives a type error?

        # original window size can be changed here
        self.originalHStart = 1
        self.originalHEnd = 658#self.detectorDimensions[0]
        self.originalVStart = 1
        self.originalVEnd = 496#self.detectorDimensions[1]      
        
        self.hstart = self.originalHStart
        self.hend = self.originalHEnd
        self.vstart = self.originalVStart
        self.vend = self.originalVEnd
        
        self.width = self.hend - self.hstart
        self.height = self.vend - self.vstart
        
        print 'width: ', self.width
        print 'height: ', self.height
        
        error = yield self.server.set_image_region(1,1,self.hstart,self.hend,self.vstart,self.vend)
        print 'image: ', error
        
        self.openVideoWindow()

        
    @inlineCallbacks
    def printTemperature(self):
        temp = yield self.server.get_current_temperature()
        print temp
    
    @inlineCallbacks
    def ionCount(self, threshold, iterations):
        avgNumberOfIons = yield self.server.count_ions(threshold, iterations)
        print avgNumberOfIons 
            
    @inlineCallbacks
    def changeEMGain(self, value):
        yield self.server.set_emccd_gain(value)

    @inlineCallbacks
    def changeExposure(self, value):
        yield self.server.set_exposure_time(value)

    
    @inlineCallbacks
    def abortVideo(self):
        self.live = False
        yield self.server.abort_acquisition()
        print 'aborted'
               
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ionCount = IonCount(reactor)
    reactor.run()
    
