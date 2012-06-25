import sys
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib import cm
import time

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from datetime import datetime

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
        
        darkIonCountButton = QtGui.QPushButton("Count Dark Ions", self)
        darkIonCountButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        darkIonCountButton.clicked.connect(self.countDarkIons) 
        
        collectDataButton = QtGui.QPushButton("Collect Data", self)
        collectDataButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        collectDataButton.clicked.connect(self.collectData)
        
        countIonSwapsButton = QtGui.QPushButton("Count Ion Swaps", self)
        countIonSwapsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        countIonSwapsButton.clicked.connect(self.countIonSwaps)
        
        exposureLabel = QtGui.QLabel()
        exposureLabel.setText('Exposure (ms): ')

        iterationsLabel = QtGui.QLabel()
        iterationsLabel.setText('Iterations: ')
        
        ionThresholdLabel = QtGui.QLabel()
        ionThresholdLabel.setText('Ion Threshold: ')

        darkIonThresholdLabel = QtGui.QLabel()
        darkIonThresholdLabel.setText('Dark Ion Threshold: ')        
        
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

        self.ionThresholdSpinBox = QtGui.QSpinBox()
        self.ionThresholdSpinBox.setMinimum(0)
        self.ionThresholdSpinBox.setMaximum(1000)
        self.ionThresholdSpinBox.setSingleStep(1)  
        self.ionThresholdSpinBox.setValue(500)     
        self.ionThresholdSpinBox.setKeyboardTracking(False)

        self.darkIonThresholdSpinBox = QtGui.QSpinBox()
        self.darkIonThresholdSpinBox.setMinimum(-1000)
        self.darkIonThresholdSpinBox.setMaximum(0)
        self.darkIonThresholdSpinBox.setSingleStep(1)  
        self.darkIonThresholdSpinBox.setValue(-200)     
        self.darkIonThresholdSpinBox.setKeyboardTracking(False)

        
        imageAnalyzedLabel = QtGui.QLabel()
        imageAnalyzedLabel.setText('Images to analyze: ')

        typIonDiameterLabel = QtGui.QLabel()
        typIonDiameterLabel.setText('Typical Ion Diameter: ')
        
        peakVicinityLabel = QtGui.QLabel()
        peakVicinityLabel.setText('Peak Vicinity: ')
        
        self.imageAnalyzedSpinBox = QtGui.QSpinBox()
        self.imageAnalyzedSpinBox.setMinimum(1)
        self.imageAnalyzedSpinBox.setMaximum(20)
        self.imageAnalyzedSpinBox.setSingleStep(1)  
        self.imageAnalyzedSpinBox.setValue(1)     
        self.imageAnalyzedSpinBox.setKeyboardTracking(False)        

        self.typIonDiameterSpinBox = QtGui.QSpinBox()
        self.typIonDiameterSpinBox.setMinimum(1)
        self.typIonDiameterSpinBox.setMaximum(20)
        self.typIonDiameterSpinBox.setSingleStep(1)  
        self.typIonDiameterSpinBox.setValue(5)     
        self.typIonDiameterSpinBox.setKeyboardTracking(False) 

        self.peakVicinitySpinBox = QtGui.QSpinBox()
        self.peakVicinitySpinBox.setMinimum(0)
        self.peakVicinitySpinBox.setMaximum(10)
        self.peakVicinitySpinBox.setSingleStep(1)  
        self.peakVicinitySpinBox.setValue(2)     
        self.peakVicinitySpinBox.setKeyboardTracking(False) 

         
         # Layout
        self.bottomPanel1 = QtGui.QHBoxLayout()
        
        self.bottomPanel1.addWidget(temperatureButton)
        self.bottomPanel1.addWidget(darkIonCountButton)
    
        self.bottomPanel1.addStretch(0)
        self.bottomPanel1.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        self.bottomPanel1.addWidget(iterationsLabel)
        self.bottomPanel1.addWidget(self.iterationsSpinBox)
        self.bottomPanel1.addWidget(ionThresholdLabel)
        self.bottomPanel1.addWidget(self.ionThresholdSpinBox)
        self.bottomPanel1.addWidget(darkIonThresholdLabel)
        self.bottomPanel1.addWidget(self.darkIonThresholdSpinBox)

        
        self.bottomPanel2 = QtGui.QHBoxLayout()

#        self.bottomPanel2.addStretch(0)
        self.bottomPanel2.addWidget(collectDataButton)
        self.bottomPanel2.addWidget(countIonSwapsButton)
        self.bottomPanel2.addWidget(imageAnalyzedLabel)
        self.bottomPanel2.addWidget(self.imageAnalyzedSpinBox)
        self.bottomPanel2.addWidget(exposureLabel)
        self.bottomPanel2.addWidget(self.exposureSpinBox)
        self.bottomPanel2.addWidget(typIonDiameterLabel)
        self.bottomPanel2.addWidget(self.typIonDiameterSpinBox)
        self.bottomPanel2.addWidget(peakVicinityLabel)
        self.bottomPanel2.addWidget(self.peakVicinitySpinBox)

        layout.addLayout(self.bottomPanel1)
        layout.addLayout(self.bottomPanel2)
        
        self.setWindowTitle('Dark Ion Analysis')  
        self.setLayout(layout)

    def printTemperature(self, evt):
        self.parent.printTemperature()
    
    def countDarkIons(self, evt):
        self.parent.countDarkIons(self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.ionThresholdSpinBox.value(), self.darkIonThresholdSpinBox.value(), self.iterationsSpinBox.value())
        
    def countIonSwaps(self, evt):
        self.parent.countIonSwaps(self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.ionThresholdSpinBox.value(), self.darkIonThresholdSpinBox.value(), self.iterationsSpinBox.value(), self.peakVicinitySpinBox.value())
    
    def collectData(self, evt):
        self.parent.collectData(self.iterationsSpinBox.value(), self.imageAnalyzedSpinBox.value())
    
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
        
        self.hstart = 1
        self.hend = 141
        self.vstart = 1
        self.vend = 52
        
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
    def collectData(self, iterations, numAnalyzedImages):
        yield self.server.collect_data((self.height + 1), (self.width + 1), iterations, numAnalyzedImages)
    
    @inlineCallbacks
    def countDarkIons(self, numAnalyzedImages, typicalIonDiameter, initialThreshold, darkThreshold, iterations):
        numKin =  (numAnalyzedImages + 1)*iterations
        darkIonCatalog = yield self.server.count_dark_ions(numKin, (self.height + 1), (self.width + 1), typicalIonDiameter, initialThreshold, darkThreshold, iterations)
        print darkIonCatalog

    @inlineCallbacks
    def countIonSwaps(self, numAnalyzedImages, typicalIonDiameter, initialThreshold, darkThreshold, iterations, peakVicinity):
        numKin =  (numAnalyzedImages + 1)*iterations
        yield self.server.count_ion_swaps(numKin, (self.height + 1), (self.width + 1), typicalIonDiameter, initialThreshold, darkThreshold, iterations, peakVicinity)
        
    
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
    
